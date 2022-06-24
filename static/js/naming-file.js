
// imports
import { focusCodeMirrorEditor, clearCodeMirror, setNewLanguageModeOfEditor } from "../script.js";
import progLanguages from './ProgrammingLanguages.js';

// DOM elements
const saveFileNameBtn = document.querySelector('.submit-new-name-btn');
const changeFileNameBtn = document.querySelector('.change-file-name-btn');
const fileNameInputElement = document.querySelector('#file-name-input');
const editFileNameContainer = document.querySelector('.name-file-container');
const fileNameLabelElement = document.querySelector('.file-name-label');

// file name input is focused once the page is successfully loaded
window.onload = () => {
    fileNameInputElement.focus();
}

saveFileNameBtn.addEventListener('click', handleSavingNewFile);

function handleSavingNewFile() {
    const newFileName = fileNameInputElement.value;
    if (newFileName == null || newFileName == undefined || newFileName === '') return;

    
    handleFileType(newFileName);
    saveNameOfTheFile(newFileName);
    toggleFileNameContainerMode();
    focusCodeMirrorEditor();
    clearCodeMirror();
}

changeFileNameBtn.addEventListener('click', () => {
    resetAllVariables();
});

// changes language mode of the editor based on extension of the new file
function handleFileType(newFileName) {
    const fileExtension = newFileName.split('.')[1];
    const modes = progLanguages();
    const mode = modes.get(fileExtension);
    setNewLanguageModeOfEditor(mode);
}

// toggles states of fileNameContainer (there are just 2 of them)
function toggleFileNameContainerMode() {
    if (editFileNameContainer.dataset.changeName === 'true') {
        editFileNameContainer.dataset.changeName = 'false';
    } else {
        editFileNameContainer.dataset.changeName = 'true';
    }
}

// saves new name of the file
function saveNameOfTheFile(newFileName) {
    fileNameLabelElement.textContent = `./${newFileName}`;
    fileNameLabelElement.dataset.nameOfFile = newFileName;
}

// setting all the elements on the page to their default values
function resetAllVariables() {
    saveNameOfTheFile('');
    toggleFileNameContainerMode();
    fileNameInputElement.focus();
}

fileNameInputElement.addEventListener('keydown', e => {
    if (e.code === 'Enter') {
        e.preventDefault();
        handleSavingNewFile();
    }
});