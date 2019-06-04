/* global $ */
var startingValue
var importValue
var editor

var downloadName = 'custom_config.json'

//Load the starting json file
  $.getJSON("json/starting_values/agent_desc.json", function( data ) { loadValues(data) });

//Loading starting values file locations
var simulation_variables, inhabitants, eclss, plants, isru, structures, fabrication, power_generation, mobility, communication, storage

//Initialize the Simulation Variables editor
var variable_editor = new window.JSONEditor(document.getElementById('variables'), {
  ajax: true,
  disable_array_reorder: true,
  schema: {$ref: 'json/schema/variables_schema.json'},
  required_by_default: true
})

//Initialize habitat starting values 
variable_editor.on('ready', function() { loadEditor( variable_editor, simulation_variables)})

//Initialize the inhabitants editor
var inhabitants_editor = new window.JSONEditor(document.getElementById('inhabitants'), {
  ajax: true,
  disable_array_reorder: true,
  schema: {$ref: 'json/schema/inhabitants_schema.json'},
  required_by_default: true
})

//Initialize inhabitants starting values
inhabitants_editor.on('ready', function(){ loadEditor( inhabitants_editor, inhabitants)})

var eclss_editor = new window.JSONEditor(document.getElementById('eclss'), {
  ajax: true,
  disable_array_reorder: true,
  schema: {$ref: 'json/schema/eclss_schema.json'},
  required_by_default: true
})

//Initialize eclss starting values
eclss_editor.on('ready', function(){ loadEditor( eclss_editor, eclss)})

var agriculture_editor = new window.JSONEditor(document.getElementById('agriculture'), {
  ajax: true,
  disable_array_reorder: true,
  schema: {$ref: 'json/schema/agriculture_schema.json'},
  required_by_default: true,
})


//Initialize agriculture starting values
agriculture_editor.on('ready', function(){ loadEditor( agriculture_editor, plants)})

//Initialize isru editor
var isru_editor = new window.JSONEditor(document.getElementById('isru'), {
  ajax: true,
  disable_array_reorder: true,
  schema: {$ref: 'json/schema/isru_schema.json'},
  required_by_default: true
})

//Initialize isru starting values
isru_editor.on('ready', function(){ loadEditor( isru_editor, isru)})

//Initialize the structure editor
var structure_editor = new window.JSONEditor(document.getElementById('structure'), {
  ajax: true,
  disable_array_reorder: true,
  schema: {$ref: 'json/schema/structure_schema.json'},
  required_by_default: true
})

//Initialize structure starting vals
structure_editor.on('ready', function(){ loadEditor( structure_editor, structures)})

//Initialize the fabrication editor
var fabrication_editor = new window.JSONEditor(document.getElementById('fabrication'), {
  ajax: true,
  disable_array_reorder: true,
  schema: {$ref: 'json/schema/fabrication_schema.json'},
  required_by_default: true
})

//Initialize fabrication starting values
fabrication_editor.on('ready', function(){ loadEditor( fabrication_editor, fabrication)})

var power_editor = new window.JSONEditor(document.getElementById('power'), {
  ajax: true,
  disable_array_reorder: true,
  schema: {$ref: 'json/schema/power_schema.json'},
  required_by_default: true
})

//Initialize power starting values
power_editor.on('ready', function(){ loadEditor( power_editor, power_generation )})

var mobility_editor = new window.JSONEditor(document.getElementById('mobility'), {
  ajax: true,
  disable_array_reorder: true,
  schema: {$ref: 'json/schema/mobility_schema.json'},
  required_by_default: true
})

//Initialize mobility starting values
mobility_editor.on('ready', function(){ loadEditor( mobility_editor, mobility)})

var communication_editor = new window.JSONEditor(document.getElementById('comms'), {
  ajax: true,
  disable_array_reorder: true,
  schema: {$ref: 'json/schema/communications_schema.json'},
  required_by_default: true
})

//Initialize communications starting values
communication_editor.on('ready', function(){ loadEditor( communication_editor, communication)})

var storage_editor = new window.JSONEditor(document.getElementById('storage'), {
  ajax: true,
  disable_array_reorder: true,
  schema: {$ref: 'json/schema/storage_schema.json'},
  required_by_default: true
})

//Initialize communications starting values
storage_editor.on('ready', function(){ loadEditor( storage_editor, storage)})

//Set the editor to a default
editor = variable_editor

//Hide the main div
var content = document.getElementById('main')
content.style.display = 'none'

function openTab (evt, tabName) {
  var i, x, tablinks
  editor = getEditor(tabName)
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

function getEditor (name) {
  var currentEditor
  switch(name) {
    case 'variables':
      currentEditor = variable_editor
      startingValue = simulation_variables
      break
    case 'inhabitants':
      currentEditor = inhabitants_editor
      startingValue = inhabitants
      break
    case 'eclss':
      currentEditor = eclss_editor
      startingValue = eclss
      break
    case 'agriculture':
      currentEditor = agriculture_editor
      startingValue = plants
      break
    case 'isru':
      currentEditor = isru_editor
      startingValue = isru
      break
    case 'structure':
      currentEditor = structure_editor
      startingValue = structures
      break
    case 'fabrication':
      currentEditor = fabrication_editor
      startingValue = fabrication
      break
    case 'power':
      currentEditor = power_editor
      startingValue = power_generation
      break
    case 'mobility':
      currentEditor = mobility_editor
      startingValue = mobility
      break
    case 'comms':
      currentEditor = communication_editor
      startingValue = communication
      break
    case 'storage':
      currentEditor = storage_editor
      startingValue = storage
      break
    default : currentEditor = variable_editor
  }
  return currentEditor
}

//function getImport(){
//}

function loadEditor (emptyEditor, jsonFile) {
  emptyEditor.setValue(jsonFile)
}

function loadValues(data) {

  console.log(data)
  simulation_variables = data.simulation_variables
  inhabitants = data.inhabitants
  eclss = data.eclss
  plants = data.plants
  isru = data.isru
  structures = data.structures
  fabrication = data.fabrication
  power_generation = data.power_generation
  mobility = data.mobility
  communication = data.communication
  storage = data.storage
  
}

// Hook up the submit button to log to the console
document.getElementById('submit').addEventListener('click', function () {
  // Get the value from the editor
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
  file.simulation_variables = variable_editor.getValue()
  file.inhabitants = inhabitants_editor.getValue()
  file.eclss = eclss_editor.getValue()
  file.plants = agriculture_editor.getValue()
  file.isru = isru_editor.getValue()
  file.structures = structure_editor.getValue()
  file.fabrication = fabrication_editor.getValue()
  file.power_generation = power_editor.getValue()
  file.mobility = mobility_editor.getValue()
  file.communication = communication_editor.getValue()
  file.storage = storage_editor.getValue()
  //TO DO: ADD together ALL Editors into one json object
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
