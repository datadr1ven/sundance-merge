function handleFiles(files) {
    const filesDisplay = document.getElementById('files-display');
    filesDisplay.innerHTML = "";
    files = [...files];
    files.forEach(loadFile);
}

function loadFile(file) {
    let reader = new FileReader();
    
    if (file.name.slice(-4).toLowerCase() === '.zip') {
        reader.readAsArrayBuffer(file);
    } else if (file.name.slice(-4).toLowerCase() === '.hy3') {
        reader.readAsBinaryString(file);
    }
    
    reader.onloadend = function() {
        let div = document.createElement('div');
        div.className = 'file-item';
        
        let p_name = document.createElement('p');
        p_name.className = 'file-item-name';
        p_name.innerText = file.name;
        div.appendChild(p_name);
        
        let p_md5 = document.createElement('p');
        p_md5.className = 'file-item-md5';
        if (file.name.slice(-4).toLowerCase() === '.zip') {
            p_md5.innerText = "md5: " + CryptoJS.MD5(CryptoJS.lib.WordArray.create(reader.result));
        } else if (file.name.slice(-4).toLowerCase() === '.hy3') {
            p_md5.innerText = "md5: " + CryptoJS.MD5(reader.result);
        }
        div.appendChild(p_md5);
        
        let p_check = document.createElement('p');
        p_check.className = 'file-item-check';
        p_check.innerText = '✓ Ready';
        div.appendChild(p_check);
        
        let hidden_file = document.createElement('input');
        hidden_file.type = 'hidden';
        hidden_file.id = "file_contents_" + file.name;
        hidden_file.value = reader.result;
        div.appendChild(hidden_file);
        
        document.getElementById('files-display').appendChild(div);
    };
}
