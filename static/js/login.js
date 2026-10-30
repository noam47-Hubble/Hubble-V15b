/* HUBBLE v15 — login / registration */
H.routes.login = async (p, root) => {
  const w = H.el(`<div class="screen"><div class="login-wrap"><div class="glass login-card">
    <img class="logo-full" src="/static/img/logo_full.png" alt="HUBIN">
    <h1>ברוכים הבאים ל-HUBIN</h1>
    <p class="lead" style="margin-bottom:18px">משתמש חדש - צור חשבון כדי להתחיל<br>משתמש חוזר - אנא הכנס את אחד המזהים שלך</p>
    <div class="row"><span class="ico">${H.ic('user', 18)}</span><input type="text" id="lgName" placeholder="שם (חובה למשתמש חדש)" autocomplete="name"></div>
    <p class="idlabel" style="margin-top:-4px">השם שתזין כאן הוא שם הרישום שלך — רק אתה תראה אותו. מה שאחרים יראו נקבע בכרטיס שלך.</p>
    <p class="idlabel"><b>מזהים</b> (בחר אחד או שניהם)</p>
    <div class="row"><span class="ico">${H.ic('phone', 18)}</span><input type="tel" id="lgPhone" placeholder="טלפון (למשל 050-1234567)" autocomplete="tel"></div>
    <div class="row"><span class="ico">${H.ic('mail', 18)}</span><input type="email" id="lgEmail" placeholder="מייל" autocomplete="email"></div>
    <div class="err" id="lgErr"></div>
    <button class="btn primary lg block" id="lgGo">כניסה</button>
    <label class="terms-chk"><input type="checkbox" id="lgAgree"><span>קראתי והבנתי שזו גרסת <b>פיילוט</b>, שהמידע שאזין אינו מוגן ויימחק בסוף הפיילוט, ואני מסכים/ה ל<a href="#" id="lgTerms">תנאי השימוש, הצהרת הפיילוט ומדיניות הפרטיות</a>.</span></label>
  </div></div></div>`);
  root.appendChild(w);
  const tl = H.$('#lgTerms', w); if (tl) tl.onclick = (e) => { e.preventDefault(); H.showTerms(); };
  const go = async () => {
    const err = H.$('#lgErr', w); err.textContent = '';
    if (!H.$('#lgAgree', w).checked) { err.textContent = 'יש לסמן שקראת ואת/ה מסכים/ה לתנאי הפיילוט'; return; }
    const body = { name: H.$('#lgName', w).value.trim(), phone: H.$('#lgPhone', w).value.trim(), email: H.$('#lgEmail', w).value.trim() };
    try {
      await H.post('/api/login', body);
      await H.refreshMe();
      if (H.sock) { H.sock.disconnect(); H.sock = null; }
      H.connectSocket();
      H.afterLogin();
    } catch (e) { err.textContent = e.message; }
  };
  H.$('#lgGo', w).onclick = go;
  w.addEventListener('keydown', e => { if (e.key === 'Enter') go(); });
  H.$('#lgName', w).focus();
};
