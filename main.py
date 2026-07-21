import hytek_parser
from hytek_parser.hy3.enums import Course
import attrs
from pyscript import document
from js import Uint8Array
from io import StringIO
from io import BytesIO
import base64
import zipfile
import hashlib

VERBOSE = True

def format_auto_quals(aq, k, pool):
    vs = vf = ""
    saq = sorted(aq, key=lambda x: x.converted_seed_time)
    if k > 0:
        vs += "\tAUTOMATIC QUALIFIERS\n"
        for entry in saq:
            entryvf = ''
            for line in pool[entry.event_number][entry.swimmers[0].last_name][entry.swimmers[0].first_name]['%02d%02d%04d' % (entry.swimmers[0].date_of_birth.month, entry.swimmers[0].date_of_birth.day, entry.swimmers[0].date_of_birth.year)]:
                vf += line
                entryvf += line
            vs += "\t(AUTO) %s, %s %s (%s), %s%s\n" % (entry.swimmers[0].last_name, entry.swimmers[0].nick_name if entry.swimmers[0].nick_name else entry.swimmers[0].first_name, entry.swimmers[0].middle_initial if entry.swimmers[0].middle_initial else "", entry.event_number, entry.converted_seed_time, entryvf.count('\n') > 0 and '\n' or '')
    return (vs, vf)

def format_k_wildcards(k, out, wl, pool):
    vs = vf = ""
    fwl = filter(lambda x: type(x.converted_seed_time) == float, wl)
    swl = sorted(fwl, key=lambda x: x.converted_seed_time)
    if k > 0:
        vs += "\t%d WILDCARDS\n" % k
        for entry in swl[:k]:
            entryvf = ''
            for line in pool[entry.event_number][entry.swimmers[0].last_name][entry.swimmers[0].first_name]['%02d%02d%04d' % (entry.swimmers[0].date_of_birth.month, entry.swimmers[0].date_of_birth.day, entry.swimmers[0].date_of_birth.year)]:
                vf += line
                entryvf += line
            vs += "\t(WILDCARD) %s, %s %s (%s), %s%s\n" % (entry.swimmers[0].last_name, entry.swimmers[0].nick_name if entry.swimmers[0].nick_name else entry.swimmers[0].first_name, entry.swimmers[0].middle_initial if entry.swimmers[0].middle_initial else "", entry.event_number, entry.converted_seed_time, entryvf.count('\n') > 0 and '\n' or '')
    if out > 0:
        vs += "\tfirst %d OUT\n" % out
        for entry in swl[k:k+out]:
            entryvf = ''
            for line in pool[entry.event_number][entry.swimmers[0].last_name][entry.swimmers[0].first_name]['%02d%02d%04d' % (entry.swimmers[0].date_of_birth.month, entry.swimmers[0].date_of_birth.day, entry.swimmers[0].date_of_birth.year)]:
                vf += line
                entryvf += line
            vs += "\t(OUT) \t%s, %s %s (%s), %s%s\n" % (entry.swimmers[0].last_name, entry.swimmers[0].nick_name if entry.swimmers[0].nick_name else entry.swimmers[0].first_name, entry.swimmers[0].middle_initial if entry.swimmers[0].middle_initial else "", entry.event_number, entry.converted_seed_time, entryvf.count('\n') > 0 and '\n' or '')
    return (vs, vf)

def accumulate_entries(hyfile, accum):
    running_accum = []
    for line in open(hyfile).readlines():
        if line[0:2] == 'C1':
            race = first_name = last_name = birthday = ''
            if len(running_accum) == 4:
                race = int(running_accum[3][38:43])
                first_name = running_accum[2][28:48].strip()
                last_name = running_accum[2][8:28].strip()
                birthday = running_accum[2][88:96]  
            elif len(running_accum) == 3 and running_accum[0][:2] == 'C1':
                race = int(running_accum[2][38:43])
                first_name = running_accum[1][28:48].strip()
                last_name = running_accum[1][8:28].strip()
                birthday = running_accum[1][88:96]
            if race not in accum:
                accum[race] = {}
            if last_name not in accum[race]:
                accum[race][last_name] = {}
            if first_name not in accum[race][last_name]:
                accum[race][last_name][first_name] = {}
            if birthday not in accum[race][last_name][first_name]:
                accum[race][last_name][first_name] = {}
            accum[race][last_name][first_name][birthday] = running_accum
            running_accum = []
        running_accum.append(line)

    race = first_name = last_name = birthday = ''
    if len(running_accum) == 4:
        race = int(running_accum[3][38:43])
        first_name = running_accum[2][28:48].strip()
        last_name = running_accum[2][8:28].strip()
        birthday = running_accum[2][88:96]
    elif len(running_accum) == 3 and running_accum[0][:2] == 'C1':
        race = int(running_accum[2][38:43])
        first_name = running_accum[1][28:48].strip()
        last_name = running_accum[1][8:28].strip()
        birthday = running_accum[1][88:96]
    if race not in accum:
        accum[race] = {}
    if last_name not in accum[race]:
        accum[race][last_name] = {}
    if first_name not in accum[race][last_name]:
        accum[race][last_name][first_name] = {}
    if birthday not in accum[race][last_name][first_name]:
        accum[race][last_name][first_name] = {}
    accum[race][last_name][first_name][birthday] = running_accum
    return accum

def render_event_table(event_num, event_data, entries_accum):
    """Render interactive HTML table for an event's qualifiers"""
    html = f'<div class="event-section">\n'
    html += f'<div class="event-header">'
    html += f'<h4>Event {event_num} ({event_data["age_min"]}-{event_data["age_max"]} {event_data["event_gender"]} {event_data["distance"]}m {event_data["stroke"]})</h4>'
    html += f'</div>\n'
    html += f'<table class="qualifiers-table">\n'
    html += f'<thead><tr><th>Status</th><th>Swimmer</th><th>Time</th></tr></thead>\n'
    html += f'<tbody>\n'
    
    # Sort all entries for display
    all_entries = sorted(
        event_data['auto_qual'] + event_data['wildcard_pool'],
        key=lambda x: x.converted_seed_time if type(x.converted_seed_time) == float else float('inf')
    )
    
    for entry in all_entries:
        swimmer = entry.swimmers[0]
        time_str = str(entry.converted_seed_time) if type(entry.converted_seed_time) == float else "--:--.-"
        
        # Determine status and styling
        if entry in event_data['auto_qual']:
            status = 'auto-qual'
            badge_class = 'badge-auto'
            badge_text = 'AUTO'
        elif entry in event_data['wildcard_pool'][:event_data.get('num_wildcards', 7)]:
            status = 'wildcard'
            badge_class = 'badge-wildcard'
            badge_text = 'WILDCARD'
        else:
            status = 'out'
            badge_class = 'badge-out'
            badge_text = 'OUT'
        
        swimmer_id = f"{event_num}_{swimmer.last_name}_{swimmer.first_name}_{swimmer.date_of_birth}"
        
        html += f'<tr class="swimmer-row {status}" data-event-num="{event_num}" data-swimmer-id="{swimmer_id}" data-status="{status}">\n'
        html += f'<td><span class="qual-badge {badge_class}">{badge_text}</span></td>\n'
        html += f'<td>{swimmer.last_name}, {swimmer.nick_name or swimmer.first_name} {swimmer.middle_initial or ""}</td>\n'
        html += f'<td class="time-display">{time_str}</td>\n'
        html += f'</tr>\n'
    
    html += f'</tbody>\n</table>\n'
    html += f'<div class="click-hint">💡 Click an AUTO qualifier to scratch them and promote the next OUT swimmer</div>\n'
    html += f'</div>\n'
    
    return html

def merge_hyfiles(the_arg):
    num_auto = int(document.getElementById('num_auto').value)
    num_wildcards = int(document.getElementById('num_wildcards').value)
    num_out = int(document.getElementById('num_out').value)

    files_div = document.getElementById('files-display')
    output_div = document.getElementById('output-container')
    download_div = document.getElementById('download-container')
    
    output_div.innerHTML = '<div class="progress-message"><span class="loading"></span> Calculating merge, standby...</div>'
    download_div.innerHTML = ""

    d = {}
    rvs = ""
    rvf = ""

    rvf += "A102Meet Entries             Hy-Tek, Ltd    SwimTopia     08012024 05:35 AMTanoan CC                                            10\n"
    rvf += "B1Sundance Championships                       Albuquerque Academy                          071920250719202505012025   0        73\n"
    rvf += "B2                                                                                          010101S1  0.00                      61\n"
    entries_accum = {}
    
    try:
        for filenum in range(files_div.children.length):
            file_div = files_div.children.item(filenum)
            file_name = file_div.children.item(0).innerText
            
            # Get file contents from hidden input (3rd child - same as original)
            file_contents = file_div.children.item(2).value
            
            if file_name[-4:].lower() == '.zip':
                ba = Uint8Array.new(file_contents)
                # Write bytearray directly instead of iterating
                with open(file_name, "wb") as f:
                    f.write(bytearray(ba))
                z = zipfile.ZipFile(file_name)
                if len(z.filelist) > 1:
                    output_div.innerHTML = f'<div class="error-message">Error: [{file_name}] contains more than one file</div>'
                    return
                if not (z.filelist[0].filename[-4:].lower() == '.hy3'):
                    output_div.innerHTML = f'<div class="error-message">Error: The file in [{file_name}] is not a .hy3 file</div>'
                    return
                z.extractall()
                file_name = z.filelist[0].filename
                file_contents = open(file_name, encoding="windows-1252").read()
                hy3_file = StringIO(file_contents)
                with open(file_name, "w") as f: 
                    for line in hy3_file.readlines():
                        f.write(line)
                
            elif file_name[-4:].lower() == '.hy3':
                hy3_file = StringIO(file_contents) 
                with open(file_name, "w") as f: 
                    for line in hy3_file.readlines():
                        f.write(line)

            rvs += "processing file [%s]\n" % file_name 

            entries_accum = accumulate_entries(file_name, entries_accum)

            hf = hytek_parser.parse_hy3(file_name)
            for event_key in hf.meet.events.keys():
                event_record = hf.meet.events[event_key]
                if event_key not in d:
                    d[event_key] = {
                        'auto_qual': [], 
                        'wildcard_pool': [], 
                        'age_min': event_record.age_min, 
                        'age_max': event_record.age_max, 
                        'event_gender': event_record.gender, 
                        'distance': event_record.distance,
                        'stroke': event_record.stroke,
                        'num_wildcards': num_wildcards
                    }
                sorted_entries = sorted(event_record.entries, key=lambda x: x.converted_seed_time)
                for (i, entry) in enumerate(sorted_entries):
                    if i <= (num_auto-1):
                        d[event_key]['auto_qual'] += [entry]
                    else:
                        d[event_key]['wildcard_pool'] += [entry]

        # Generate HTML output with interactive tables
        html_output = '<div class="success-message">✓ Merge complete! Click AUTO qualifiers below to scratch them and promote OUT swimmers.</div>\n'
        
        for i in range(1, 81):
            if i not in d:
                pass
            else:
                html_output += render_event_table(i, d[i], entries_accum)
                (vs, vf) = format_auto_quals(d[i]['auto_qual'], num_auto, entries_accum)
                rvs += vs
                rvf += vf
                (vs, vf) = format_k_wildcards(num_wildcards + ((num_auto*files_div.children.length) - len(d[i]['auto_qual'])), num_out, d[i]['wildcard_pool'], entries_accum)
                rvs += vs
                rvf += vf

        output_div.innerHTML = html_output
        
        # Create download button
        s = base64.b64encode(rvf.encode("windows-1252")).decode('ascii')
        download_div.innerHTML = f'<a href="data:application/octet-stream;base64,{s}" download="entry_file.hy3" class="download-link">📥 Download HY3 Entry File</a>'
        
        # Attach click handlers for interactive adjustment
        try:
            from js import attachQualifierClickHandlers
            attachQualifierClickHandlers()
        except:
            pass
    
    except Exception as e:
        output_div.innerHTML = f'<div class="error-message">Error: {str(e)}</div>'
        import traceback
        print(traceback.format_exc())
