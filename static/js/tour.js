/* HUBIN — guided tour (slides): login, personal card, my messages & contacts, and above all working inside a hub */
(function () {
  const esc = H.esc;
  const ic = (n, s) => H.ic(n, s || 18);

  /* ---- small CSS-drawn illustrations ---- */
  const A = {
    welcome: () => '<div class="ta-logo"><img src="/static/img/logo_full.png" alt="HUBIN"></div>',
    login: () => '<div class="ta-flow"><div class="ta-chip">' + ic('user') + '<b>שם</b><span>טלפון או מייל</span></div><i>→</i><div class="ta-chip">' + ic('lock') + '<b>סיסמה</b><span>לא חובה</span></div><i>→</i><div class="ta-chip on">' + ic('check') + '<b>כניסה</b><span>המכשיר נזכר</span></div></div>',
    card: () => '<div class="ta-card"><div class="ta-av">ד</div><div class="ta-lines">' +
      [['שם', 'דנה כהן'], ['תפקיד', 'מנהלת שיווק'], ['חברה', 'Acme'], ['טלפון', '050-•••']].map((r, i) => '<div class="ta-ln"><span>' + r[0] + '</span><b>' + r[1] + '</b><em class="' + (i < 3 ? 'on' : '') + '">' + ic(i < 3 ? 'eye' : 'eyeoff', 15) + '</em></div>').join('') + '</div></div>',
    modes: () => '<div class="ta-flow"><div class="ta-chip"><b>כרטיס עסקי</b><span>שם · תפקיד · חברה</span></div><div class="ta-chip"><b>כרטיס חברתי</b><span>כינוי · תמונה · רשתות</span></div></div><div class="ta-flow" style="margin-top:10px"><div class="ta-chip on"><span class="dotg"></span><b>פתוח לתקשורת</b></div><div class="ta-chip"><span class="dotr"></span><b>צופה בלבד</b></div></div>',
    home: () => '<div class="ta-srch">חיפוש האב לפי שם, מספר או בעל ההאב</div><div class="ta-pills"><span class="on">הכל</span><span>מועדפים</span><span>קרובים</span><span>שלי</span><span>סוג</span></div><div class="ta-list">' + [['CyberTech Israel 2026', 'מקצועי', 1], ['בלומפילד שער 5', 'חברתי', 0], ['קפה ספרים', 'עסקי', 0]].map(r => '<div class="ta-row"><i>' + ic('star', 15) + '</i><b>' + r[0] + '</b><span>' + r[1] + '</span></div>').join('') + '</div><div class="ta-fab">+</div>',
    enter: () => '<div class="ta-bcard"><div class="ta-bc-t">SIDEC 2026</div><div class="ta-bc-s">כנס תעשיית הסייבר</div><div class="ta-bc-n"><div><small>נרשמים</small><b>120</b></div><div><small>נוכחים</small><b>43</b></div></div><div class="ta-bc-b">כניסה להאב</div></div><div class="ta-flow" style="margin-top:10px"><div class="ta-chip on"><span class="dotg"></span><b>נוכח פיזית</b></div><div class="ta-chip"><span class="dota"></span><b>מרחוק</b></div></div>',
    layout: () => '<div class="ta-hub"><div class="ta-hb">שם ההאב · ★ · שיתוף<small>ניהול ההאב · מרחוק</small></div><div class="ta-hm"><div class="c3 l"><b>חלונות רשות</b><small>עד 4 · שליש שמאלי</small></div><div class="c3 m"><b>הודעות</b><small>כללי / פרטי</small></div><div class="c3 r"><b>רשימת האנשים</b><small>ר׳ רשומים · נ׳ נוכחים</small></div></div><div class="ta-hf"><span>תוכנית</span><span>ספונסרים</span><span>מפה</span><i></i><span class="m">הודעות</span><span class="m">אנשים</span></div></div>',
    windows: () => '<div class="ta-flow wrap"><div class="ta-chip"><span class="pinb">' + ic('pin', 14) + '</span><b>תצוגה קבועה</b><span>חלון אחד תמיד פתוח</span></div><div class="ta-chip"><b>עד 4 חלונות</b><span>חמישי? סגור אחד</span></div><div class="ta-chip"><span class="pinb">' + ic('expand', 14) + '</span><b>הגדלה</b><span>לחיצה שנייה או על הלוגו מחזירה</span></div></div>',
    people: () => '<div class="ta-card"><div class="ta-av">ר</div><div class="ta-lines"><div class="ta-ln"><span>רן אביב</span><b>מנכ״ל · Acme</b></div></div></div><div class="ta-flow" style="margin-top:10px"><div class="ta-chip on"><b>שמור באנשי הקשר</b></div><div class="ta-chip"><b>הודעה פרטית</b></div></div>',
    menu: () => '<div class="ta-menu">' + ['דוחות', 'אל תציג כרטיס ביקור בכניסה', 'שתף ההאב', 'כבה התרעות קוליות', 'חזרה להאב'].map((t, i) => '<div class="' + (i === 4 ? 'pri' : '') + '">' + t + '</div>').join('') + '</div>',
    msgs: () => '<div class="ta-chat"><div class="in">שלום, נפגש בדוכן 12?</div><div class="out">מעולה, בעוד רבע שעה</div></div><div class="ta-flow" style="margin-top:8px"><div class="ta-chip on"><b>הוזמנת לקבוצה ״צוות״</b><span>צרף אותי · דחה הצטרפות</span></div></div>',
    contacts: () => '<div class="ta-flow wrap"><div class="ta-chip"><b>אנשי קשר</b><span>שורות או ריבועים · מי פעיל עכשיו</span></div><div class="ta-chip"><b>קבוצות</b><span>הודעה לכולם · מי לידי</span></div><div class="ta-chip on"><b>+ חיפוש אנשים</b><span>לפי שם, טלפון/מייל או האב</span></div></div>',
    done: () => '<div class="ta-logo"><img src="/static/img/logo_full.png" alt="HUBIN"></div>',
  };

  const SLIDES = [
    { t: 'ברוכים הבאים ל-HUBIN', art: 'welcome', g: 'start', p: ['האב הוא מרחב חי למפגש חברתי באירוע, עסק או קהילה: רואים מי שם, מתקשרים, מקבלים ומעלים את כל המידע במקום אחד.', 'ההדרכה הקצרה מסבירה את דרך העבודה. אפשר לדלג בכל רגע ולחזור אליה מחלון ההגדרות במסך הראשי של האפליקציה.'] },
    { t: 'כניסה', art: 'login', g: 'start', p: ['נכנסים עם שם וטלפון או מייל בכניסה ראשונה. סיסמה אפשר להגדיר בחלון ההגדרות במסך הראשי — מרגע שהוגדרה היא תדרש בכל פתיחה חדשה של האפליקציה ואחרי יותר מדקה ברקע.', 'המכשיר זוכר אותך, ואפשר לצאת מהמערכת מהמסך הראשי ולחזור בהקשת ׳מזהה׳ בלבד.'] },
    { t: 'מסך הבית', art: 'home', g: 'home', p: ['זה המסך המרכזי של האפליקציה. עיקר המסך הוא רשימת המתחמים (האבים) שנפתחו במערכת. אפשר לחפש האבים לפי שם או מספר, לסמן מועדפים ולסנן ״קרובים״ לפי מיקום (200 מ׳, 1 ק״מ או 2 ק״מ) ולפי סוג ההאב (חברתי, מקצועי או עסקי) והאבים שלי.', 'הכפתור + פותח האב חדש. כניסה להאב קיים — לחיצה על השורה/ריבוע של ההאב. חובה למלא כרטיס אישי אחד לפחות כדי להיכנס להאבים!', 'בצד ימין למעלה מופיע הלוגו של האפליקציה המשמש גם ככפתור חזרה ל׳מסך קודם׳. לידו במסך הבית נמצא גם כפתור היציאה.', 'מצד שמאל למעלה מופיע השם שלך (רק אתה רואה אותו) והכרטיס האישי הפעיל שלך. לידו סימן פתיחת חלון הניהול.', 'מלבד החלק המרכזי של ההאבים נמצאים בחלון הראשי גם כפתורים לאזורים האישיים שלך — ׳הכרטיסים שלי׳, ׳ההודעות הפרטיות שלי׳ ו׳אנשי הקשר שלי׳. ההדרכה עליהם בהמשך.'] },
    { t: 'כרטיס אישי', art: 'card', g: 'card', p: ['לפני הכניסה להאב מגדירים כרטיס אישי: זה מה שאחרים רואים עליך בכל האב שנכנסת אליו. ניתן לבחור בין כרטיס ׳חברתי׳ לכרטיס ׳עסקי׳ לפי סוג הפעילות שאתה נכנס אליו. רק כרטיס אחד יהיה פעיל בו זמנית.', 'אפשר להחזיק מספר כרטיסים ולהחליף את הכרטיס הפעיל מהשם שבפינה העליונה.', 'בכל כרטיס יש שדות חובה (בדרך כלל רק שם שתרצה שיוצג) ושדות רשות. ניתן למלא את כל השדות ולבחור בחלונית משמאל לשדה אם שדה זה יהיה חשוף לקהל או לא. ניתן לשנות את הבחירה ולעדכן את הכרטיסים בכל שלב.', 'את שם הכרטיס רק אתה רואה (מופיע במסך הכרטיסים שלך) על מנת שתוכל לזכור אותו. בחירת השם חופשית.'] },
    { t: 'סוגי כרטיס ומצב תקשורת', art: 'modes', g: 'card', p: ['כרטיס עסקי מתאים להאבים מקצועיים ועסקיים; כרטיס חברתי להאבים חברתיים.', 'כרטיס פתוח לתקשורת מאפשר לקבל ולשלוח הודעות. כרטיס סגור (״צופה״) רואה בלבד.'] },
    { t: 'כניסה להאב', art: 'enter', g: 'hub', p: ['בכניסה להאב מוצג קודם כרטיס הביקור של ההאב. ״כניסה להאב״ מכניסה אותך להאב עצמו. אפשר לסמן בתחתית החלון שלא להציג שוב את כרטיס הביקור, לצורך כניסה מהירה להאב.', 'בכרטיס הביקור (ובהאב עצמו) ניתן להוסיף את ההאב למועדפים ולשתף את ההאב עם אחרים.', 'בהאבים עם אימות נוכחות מבקשים מיקום או קוד: מי שנמצא פיזית מסומן ״נוכח פיזית״, ואחרת ״נכנס מרחוק״ (לחיצה על התג מאפשרת לנסות שוב).'] },
    { t: 'מסך ההאב', art: 'layout', g: 'hub', p: ['בחלק העליון של ההאב יש את שם ההאב ופרטי ניהול ומידע. לחיצה על שם ההאב פותחת שוב את כרטיס הביקור שלו.', 'החלק המרכזי של ההאב מיועד למסכי תקשורת ומסכי מידע שמנהל ההאב הוסיף.', 'מסך ההאב נפתח כשהחלונות שלו סגורים. בתחתית ההאב יש את כפתורי פתיחה/סגירה של החלונות: ״רשימת האנשים״ ו״הודעות״ מימין, וחלונות הרשות של המנהל משמאל.', 'במחשב: האנשים וההודעות מימין ובאמצע, חלונות הרשות בצד שמאל. בנייד: כל חלון על מסך משלו וגוללים בין המסכים. ניתן להגדיל כל מסך שבשימוש.'] },
    { t: 'חלונות רשות', art: 'windows', g: 'hub', p: ['חלונות הרשות הם חלונות שהגדיר מנהל ההאב ומשמשים להעברת מידע. ניתן לפתוח עד 4 חלונות רשות בו זמנית.', 'כל כפתור בתחתית פותח חלון מידע (תוכנית, מפה, ספונסרים ועוד).', 'אם מנהל ההאב הגדיר חלון ב-״תצוגה קבועה״ הוא יהיה פתוח כל הזמן.', 'ב״לוח שיתופי״ כל המשתתפים יכולים להוסיף כיתוב, תמונה או וידאו.'] },
    { t: 'אנשים והודעות בהאב', art: 'people', g: 'hub', p: ['ברשימת האנשים אפשר לעבור בין ״רשומים להאב״ ל״נוכחים בהאב״, לחפש ולעבור בין שורות לריבועים.', 'לחיצה על אדם פותחת את כרטיסו: משם שומרים אותו באנשי הקשר או שולחים הודעה פרטית.', 'בחלון ההודעות: ״כללית״ לכולם ו״פרטית״ לשיחות אישיות בהאב. מנהל ההאב יכול להצמיד הודעה.'] },
    { t: 'ניהול ההאב (התפריט העליון)', art: 'menu', g: 'hub', p: ['הכפתור ״ניהול ההאב״ בראש המסך פותח תפריט: דוחות (אפשר לשמור ולשתף כ-PDF), בחירה אם להציג כרטיס ביקור בכניסה, שיתוף ההאב וכיבוי התרעות קוליות בהאב הזה.', 'למנהל ההאב יש בנוסף כניסה למסך הניהול המלא. ״חזרה להאב״ או לחיצה על הלוגו סוגרים את התפריט.'] },
    { t: 'ההודעות הפרטיות שלי — במסך הראשי', art: 'msgs', g: 'msgs', p: ['״הודעות פרטיות״ מרכז את כל השיחות שלך, מכל ההאבים: אנשי קשר וקבוצות, בשורות או בריבועים.', 'בשיחה רואים את כרטיס הביקור של האדם או של הקבוצה. כשמצרפים אותך לקבוצה מופיעה הזמנה — ״צרף אותי״ או ״דחה הצטרפות״; אפשר גם לעזוב קבוצה בכל עת.', 'אפשר גם לשלוח הודעה בווטסאפ או באפליקציה אחרת ולחזור ל-HUBIN.'] },
    { t: 'אנשי הקשר והקבוצות', art: 'contacts', g: 'contacts', p: ['״אנשי הקשר שלי״ שומר את מי שהכרת. הכפתור + בלשונית אנשי קשר מחפש אנשים רשומים לפי שם, טלפון/מייל או מתוך האב, וכך מצרפים בלחיצה.', 'בקבוצה: שולחים הודעה לכולם, רואים מי פעיל עכשיו, ״איפה הם עכשיו״ ו״מי לידי״ (בטווח שבוחרים ובכפוף למיקום המכשיר).'] },
    { t: 'מוכנים!', art: 'done', g: 'end', p: ['זהו — כרטיס אישי, האב ראשון, ושיחה.', 'את ההדרכה אפשר להפעיל שוב בכל עת מההגדרות (גלגל השיניים) או מתפריט ״ניהול ההאב״ בתוך האב.'] },
  ];

  H.tour = (opts = {}) => {
    if (document.querySelector('.tour-ov')) return;
    let i = Math.max(0, Math.min(SLIDES.length - 1, opts.start || 0));
    if (opts.group) { const k = SLIDES.findIndex(s => s.g === opts.group); if (k >= 0) i = k; }
    const ov = H.el('<div class="tour-ov"><div class="tour"><button class="tour-x" aria-label="סגור">✕</button><div class="tour-art"></div><h2></h2><div class="tour-body"></div><div class="tour-dots"></div><div class="tour-nav"><button class="btn" id="tPrev">הקודם</button><button class="btn" id="tSkip">דלג</button><button class="btn primary" id="tNext">הבא</button></div></div></div>');
    const $ = s => H.$(s, ov);
    const finish = () => { ov.remove(); document.removeEventListener('keydown', onKey); if (opts.auto || !H.pref('tour_seen')) H.setPref('tour_seen', true); };
    const draw = () => {
      const s = SLIDES[i];
      $('.tour-art').innerHTML = A[s.art]();
      $('h2').textContent = s.t;
      $('.tour-body').innerHTML = s.p.map(t => '<p>' + esc(t) + '</p>').join('');
      $('.tour-dots').innerHTML = SLIDES.map((_, k) => '<i class="' + (k === i ? 'on' : '') + '" data-k="' + k + '"></i>').join('');
      $('#tPrev').style.visibility = i ? 'visible' : 'hidden';
      $('#tNext').textContent = i === SLIDES.length - 1 ? 'סיום' : 'הבא';
      $('#tSkip').classList.toggle('hidden', i === SLIDES.length - 1);
      H.$$('.tour-dots i', ov).forEach(d => d.onclick = () => { i = +d.dataset.k; draw(); });
    };
    const next = () => { if (i >= SLIDES.length - 1) return finish(); i++; draw(); };
    const prev = () => { if (i) { i--; draw(); } };
    const onKey = e => { if (e.key === 'Escape') finish(); else if (e.key === 'ArrowLeft') next(); else if (e.key === 'ArrowRight') prev(); };
    $('#tNext').onclick = next; $('#tPrev').onclick = prev; $('#tSkip').onclick = finish; $('.tour-x').onclick = finish;
    document.addEventListener('keydown', onKey);
    document.body.appendChild(ov);
    draw();
  };
})();
