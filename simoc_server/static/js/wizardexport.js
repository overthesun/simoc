function exportConfiguration() {

  var date = new Date().toLocaleString();

  console.log(formDict());
  var filename ="simoc_params" + date + ".txt";
  var input = JSON.stringify(formDict()); 

  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(input));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}
