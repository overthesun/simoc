/* global $ */
var startingValue
var startingData
var importValue
var downloadName = 'custom_config.json'
var editor

// editors object contains all editors
var editors = {
  simulation_variables: {},
  inhabitants: {},
  eclss: {},
  plants: {},
  isru: {},
  structures: {},
  fabrication: {},
  power_generation: {},
  mobility: {},
  communication: {},
  storage: {}
}

// load default data from root directory
fetch('../../agent_desc.json')
  .then(response => response.json())
  .then(data => {
    buildEditors(data)
    startingData = data
  })

// build editors for each section using loaded data
const buildEditors = (data) => {
  currencySchema = data.schemas.currency

  Object.keys(editors).forEach(section => {
    var sectionSchema = data.schemas[section]
    sectionSchema.definitions.currency = currencySchema
    var startVal = data[section]

    editors[section] = new window.JSONEditor(document.getElementById(section), {
      disable_array_reorder: true,
      schema: sectionSchema,
      required_by_default: true,
      remove_empty_properties: true,
      show_opt_in: true,
      startval: startVal
    })
  })

  // Set editor to variables by default
  editor = editors['simulation_variables']

  // Hook up the validation indicator to update its
  // status whenever the editor changes
  editor.on('change', function () {
    // Get an array of errors from the validator
    var errors = editor.validate()

    var indicator = document.getElementById('valid_indicator')

    // Not valid
    if (errors.length) {
      indicator.style.color = 'red'
      indicator.textContent = 'Not valid input'
    // Valid
    } else {
      indicator.style.color = 'green'
      indicator.textContent = 'Valid input'
    }
  })

}

//Hide the main div
var content = document.getElementById('main')
content.style.display = 'none'

function openTab (evt, tabName) {
  var i, x, tablinks
  editor = editors[tabName]
  startingValue = startingData[tabName]
  // editor = getEditor(tabName)
  //getImport()
  content.style.display = 'block'
  x = document.getElementsByClassName('editor')
  for (i = 0; i < x.length; i++) {
      x[i].style.display = 'none'
  }
  tablinks = document.getElementsByClassName('tablink')
  for (i = 0; i < x.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(' highlighted', '')
  }
  document.getElementById(tabName).style.display = 'block'
  evt.currentTarget.className += ' highlighted'
  downloadName = 'agent_desc.json'
  console.log(startingValue)
  console.log(importValue)
}

function loadEditor (emptyEditor, jsonFile) {
  emptyEditor.setValue(jsonFile)
}

// Hook up the submit button to log to the console
document.getElementById('submit').addEventListener('click', function () {
  
  // Get the values from the editor
  console.log(editor.getValue())
  file = {"simulation_variables" : {},
          "inhabitants" : {},
          "eclss" : {},
          "plants" : {},
          "isru" : {},
          "structures" : {},
          "fabrication" : {},
          "power_generation" : {},
          "mobility" : {},
          "communication" : {},
          "storage" : {}}
  Object.keys(editors).forEach(section => {
    file[section] = editors[section].getValue()
  })

  // Initiate download by creating a button, then remove it
  var data = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(file, null, 2))
  var downloadAnchorNode = document.createElement('a')
  downloadAnchorNode.setAttribute('href', data)
  downloadAnchorNode.setAttribute('download', downloadName)
  document.body.appendChild(downloadAnchorNode) // required for firefox
  downloadAnchorNode.click()
  downloadAnchorNode.remove()
})

// Hook up the Restore to Default button
document.getElementById('restore').addEventListener('click', function () {
  if(importValue){
    editor.setValue(importValue)
  }else{
    editor.setValue(startingValue)
  }
})

// Function for restoring the starting values to SIMOC defaults
document.getElementById('restore_defaults').addEventListener('click', function () {
  loadEditor(editor, startingValue)
  $('#selectFiles').val('')
})

// Hook up import button
document.getElementById('import').onclick = function () {
  var files = document.getElementById('selectFiles').files
  console.log(files)
  if (files.length <= 0) {
    return false
  }
  var fr = new window.FileReader()
  fr.onload = function (e) {
    console.log(e)
    importValue = JSON.parse(e.target.result)
    editor.setValue(importValue)
  }
  fr.readAsText(files.item(0))
}


