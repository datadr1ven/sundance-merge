# Sundance Championships - Entries Merge Tool

A browser-based tool that transforms district swim meet advancers files into a championship meet entry file.

## Features

- **Upload Multiple Files**: Support for HY3 and zipped HY3 format files from 2-3 qualifying meets
- **Configurable Qualification Rules**: Adjust auto-qualifiers, wildcards, and out-list counts per event
- **Interactive Qualifier Adjustment**: Click to scratch auto-qualifiers and automatically promote swimmers from the OUT list
- **Per-Event Control**: Manage qualifications individually for each event (1-80)
- **Beautiful UI**: Modern, responsive design with intuitive workflow
- **One-Click Export**: Download the merged championship entry file in HY3 format

## How to Use

1. **Upload Files**: Select 2-3 HY3 or zipped HY3 advancers files from your qualifying meets
2. **Set Rules**: Configure the number of auto-qualifiers, wildcards, and out swimmers to display
3. **Merge**: Click the merge button to process all files
4. **Adjust (Optional)**: Click on any AUTO qualifier to scratch them; the next OUT swimmer will automatically be promoted
5. **Download**: Export your merged championship entry file

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Backend**: Python with PyScript
- **Libraries**: 
  - `hytek_parser` - For parsing HY3 swim meet files
  - `CryptoJS` - For MD5 verification of uploaded files

## Installation

This tool runs entirely in the browser via GitHub Pages. No installation needed!

Visit: `https://datadr1ven.github.io/sundance-merge`

## File Format Support

- `.hy3` - HY-TEK Meet Manager format (SwimTopia advancers export)
- `.zip` - ZIP archives containing a single HY3 file

## Notes

- All processing happens in your browser; files are not uploaded to any server
- Generated entry file includes ALL swimmers (autos, wildcards, and out list) for review before final submission
