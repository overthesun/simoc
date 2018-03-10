function gotourl(url) {
    window.location.href =  window.location.href+getport()+url;
}
function getport(){
    if(window.location.port!="0") return ":"+window.location.port
}
function isEmpty(str) {
    return (!str || 0 === str.length);
}
