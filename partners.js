async function loadPartners(){
    try{
        const response=await fetch('/api/partners/');
        const data=await response.json();
        const partnersContainer=document.getElementById('partners-container');
        if(!partnersContainer)return;
        if(data.partners&&data.partners.length>0){
            partnersContainer.innerHTML=data.partners.map(partner=>{
                const logoHtml=partner.logo?'<img src="'+partner.logo+'" alt="'+partner.nom+'">':'';
                return'<div class="partner-item">'+'<a href="'+(partner.lien||'#')+'" target="_blank" title="'+(partner.description||partner.nom)+'">'+logoHtml+'</a></div>';
            }).join('');
        }else{
            partnersContainer.innerHTML='<p>Aucun partenaire.</p>';
        }
    }catch(e){
        console.error(e);
    }
}

async function initContactForm(){
    const contactForm=document.getElementById('contact-form');
    const contactResult=document.getElementById('contact-result');
    if(!contactForm)return;
    contactForm.addEventListener('submit',async(e)=>{
        e.preventDefault();
        const formData={
            nom:document.getElementById('contact-name').value,
            email:document.getElementById('contact-email').value,
            type_demande:document.getElementById('contact-type').value,
            message:document.getElementById('contact-message').value
        };
        contactResult.style.display='block';
        contactResult.className='info-message';
        contactResult.style.background='rgba(0,198,255,0.1)';
        contactResult.style.border='1px solid var(--primary-color)';
        contactResult.style.color='var(--primary-color)';
        contactResult.textContent='Envoi...';
        try{
            const response=await fetch('/api/contact/',{
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify(formData)
            });
            const data=await response.json();
            if(data.success){
                contactResult.className='success-message';
                contactResult.style.background='rgba(57,255,20,0.2)';
                contactResult.style.border='1px solid var(--success-color)';
                contactResult.style.color='var(--success-color)';
                contactResult.textContent='OK '+data.message;
                contactForm.reset();
                setTimeout(()=>{contactResult.style.display='none'},5000);
            }else{
                contactResult.className='error-message';
                contactResult.style.background='rgba(255,0,127,0.1)';
                contactResult.style.border='1px solid var(--danger-color)';
                contactResult.style.color='var(--danger-color)';
                contactResult.textContent='Erreur: '+(data.error||'Erreur');
            }
        }catch(e){
            console.error(e);
            contactResult.className='error-message';
            contactResult.textContent='Erreur de connexion';
        }
    });
}

document.addEventListener('DOMContentLoaded',()=>{
    const floatingAddFilterBtn=document.getElementById('floating-add-filter');
    const modal=document.getElementById('add-filter-modal');
    if(floatingAddFilterBtn&&modal){
        floatingAddFilterBtn.addEventListener('click',()=>{
            modal.style.display='flex';
        });
    }
    const filterSelect=document.getElementById('add-extra-filter-select');
    if(filterSelect){
        filterSelect.addEventListener('change',async function(){
            const filterType=this.value;
            if(!filterType)return;
            if(typeof addFilter==='function'){
                addFilter(filterType);
            }
            this.value='';
        });
    }
    loadPartners();
    initContactForm();
});
