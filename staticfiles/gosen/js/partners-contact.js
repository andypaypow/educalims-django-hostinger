document.addEventListener('DOMContentLoaded',function(){
    var f=document.getElementById('floating-add-filter');
    var m=document.getElementById('add-filter-modal');
    f&&m&&(f.onclick=function(){m.style.display='flex'});
    var s=document.getElementById('add-extra-filter-select');
    s&&s.addEventListener('change',function(){
        var t=this.value;
        t&&(typeof addFilter)=='function'&&addFilter(t),this.value='';
    });
});
