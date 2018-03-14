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
  var elem = JSON.stringify($(document.getElementById('wizardform')).serializeArray());
  //var elem = document.getElementById("wizardform");
  /*var text = "";
  console.log(elem.length);

  for (var index = 0; index < elem.length; index++) {
      text += String(elem.elements[index].id) + ":" + String(elem.elements[index].checked) + "\n";
      console.log(String(elem.elements[index].checked) + "\n");
    
  }

  return text;*/
  return elem;
}


function exportConfiguration() {

  var filename ="test.txt";
  var input = getFormValues();

  console.log(input);

  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(input));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}

/*document.getElementById('finalize-step').addEventListener('click',finalizeExport);

function finalizeExport(){

    var permanentBox = document.getElementById('permanent-checkbox').value;

    if(permanentBox){
        //Disable The Text Box
    }
}*/