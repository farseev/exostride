/* ExoStride — minimal progressive enhancement */
(function(){
  /* Opened straight off disk (file://)? Directory URLs have no index resolution,
     so point every internal link at the actual file. No effect when hosted. */
  if(location.protocol==='file:'){
    document.querySelectorAll('a[href]').forEach(function(a){
      var h=a.getAttribute('href');
      if(!h||/^([a-z]+:|#|\/\/)/i.test(h))return;
      var parts=h.split('#'), p=parts[0];
      if(p===''||p==='./'||/\/$/.test(p))a.setAttribute('href',p+'index.html'+(parts[1]?'#'+parts[1]:''));
    });
  }

  var nav=document.getElementById('nav'), b=document.getElementById('burger');
  if(b){b.addEventListener('click',function(){var o=nav.classList.toggle('open');
    b.setAttribute('aria-expanded',o);});}
  document.querySelectorAll('.nav-links a').forEach(function(a){
    a.addEventListener('click',function(){nav.classList.remove('open');
      b&&b.setAttribute('aria-expanded','false');});});

  /* language switcher: close on Escape / outside click; remember nothing (no cookies) */
  var sw=document.querySelector('.langsw');
  if(sw){
    document.addEventListener('click',function(e){if(sw.open&&!sw.contains(e.target))sw.open=false;});
    sw.addEventListener('keydown',function(e){if(e.key==='Escape'&&sw.open){sw.open=false;sw.querySelector('summary').focus();}});
    sw.querySelectorAll('a[hreflang]').forEach(function(a){a.addEventListener('click',function(){
      if(window.gtag)gtag('event','language_switch',{to:a.getAttribute('hreflang'),from:document.documentElement.lang});});});
  }

  var R=document.querySelectorAll('.reveal');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(x){
      if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}});},
      {threshold:0,rootMargin:'0px 0px -8% 0px'});
    R.forEach(function(el){io.observe(el);});
    /* safety net: never leave content invisible */
    setTimeout(function(){R.forEach(function(el){el.classList.add('in');});},4000);
    window.addEventListener('beforeprint',function(){R.forEach(function(el){el.classList.add('in');});});
  } else {R.forEach(function(el){el.classList.add('in');});}

  /* WhatsApp clicks -> GA4 */
  document.querySelectorAll('[data-wa]').forEach(function(a){
    a.addEventListener('click',function(){
      if(window.gtag)gtag('event','whatsapp_click',{placement:a.getAttribute('data-wa'),
        page_location:location.href});});});

  /* fitting form -> pre-filled WhatsApp handoff (no data leaves the browser) */
  var f=document.getElementById('f-try');
  if(!f)return;
  /* WhatsApp message labels come from the page's hidden .l10n block (translated per language) */
  function L(k,d){var e=document.querySelector('#t-l10n [data-k="'+k+'"]');return e?e.textContent.trim():d;}
  function ref(){return 'EXO-'+Math.random().toString(36).slice(2,6).toUpperCase()+
    Date.now().toString().slice(-3);}
  f.addEventListener('submit',function(ev){
    ev.preventDefault();
    var ok=true;
    ['t-name','t-tel','t-mail'].forEach(function(id){
      var el=document.getElementById(id);
      var bad=!el.value.trim()||(el.type==='email'&&!/^\S+@\S+\.\S+$/.test(el.value));
      el.style.borderColor=bad?'var(--crimson)':'var(--hair)';
      if(bad)ok=false;});
    var err=document.getElementById('t-err');
    if(!ok){err.classList.add('show');return;}
    err.classList.remove('show');
    var r=ref(), s=document.getElementById('t-scn');
    document.getElementById('t-ref').textContent=L('ref','Ref')+' '+r;
    var lines=[L('hi',"Hi, I'd like to learn about ExoStride and book a fitting."),
         L('ref','Ref')+': '+r,
         L('name','Name')+': '+document.getElementById('t-name').value,
         L('scenario','Scenario')+': '+s.options[s.selectedIndex].text,
         L('date','Date')+': '+(document.getElementById('t-date').value||'-'),
         L('tel','Tel')+': '+document.getElementById('t-tel').value,
         L('email','Email')+': '+document.getElementById('t-mail').value,
         L('notes','Notes')+': '+(document.getElementById('t-note').value||'-')];
    document.getElementById('t-wa').href='https://wa.me/6591227009?text='+
      encodeURIComponent(lines.join('\n'));
    document.getElementById('t-ok').classList.add('show');
    if(window.gtag)gtag('event','generate_lead',{ref:r,scenario:s.value});
  });
})();
