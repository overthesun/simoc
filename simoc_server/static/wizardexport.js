/*function exportConfiguration(filename, formID){
  var input = getFormValues(formID);

  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}

function getFormValues(formID){
  var elem = document.getElementById('wizardform');
  var text = "";
  var index;
  for(index =0; index<elem.length; index++){
    text += elem.element[index].value + "\n";
  }
}*/

function getFormValues(){
    var elem = document.getElementById("wizardform");
    var text = "";
    console.log(elem.length);

    for (var index = 0; index < elem.length; index++) {
        text += elem.elements[index].name + ":" + elem.elements[index].value + "\n";
        console.log(elem.elements[index].name);
    }

  return text;
}


function exportConfiguration() {

  var filename ="text.txt";
  var input = getFormValues();

  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(input));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}

document.getElementById('finalize-step').addEventListener('click',finalizeExport);

function finalizeExport(){

    var permanentBox = document.getElementById('permanent-checkbox').value;

    if(permanentBox){
        exportConfiguration();
    }
}