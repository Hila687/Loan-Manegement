# העלאה לפרודקשן – גמ"ח חסדי יעקב

המערכת נבנית כ־**Docker image אחד**: הוא בונה את ממשק ה־Vue ומריץ את Django עם gunicorn, שמגיש גם את האתר וגם את ה־API מאותה כתובת (`/api/...`). אין צורך ב־CORS או בשני שרתים נפרדים.

```
דפדפן ──HTTPS──▶ Caddy (תעודה אוטומטית) ──▶ web: Django + gunicorn ──▶ PostgreSQL
                                                │
                                   /data/media (טפסים חתומים)
reminders: תזכורות תשלום כל בוקר        backup: גיבוי כל לילה ל־/data/backups
```

יש שתי דרכים להעלות. **דרך א'** (שרת משלכם) היא הזולה והפשוטה ביותר לפיילוט.

---

## דרך א' – שרת משלכם (VPS) עם docker compose

**מה צריך:** שרת Ubuntu קטן (2GB זיכרון מספיקים, למשל Hetzner / DigitalOcean / Linode), ושם דומיין (למשל `gemach.example.org`).

1. **הפניית הדומיין:** אצל ספק הדומיין יוצרים רשומת `A` שמצביעה לכתובת ה־IP של השרת.
2. **התקנת Docker בשרת:**
   ```bash
   curl -fsSL https://get.docker.com | sh
   ```
3. **הורדת הקוד:**
   ```bash
   git clone https://github.com/Hila687/Loan-Manegement.git gemach && cd gemach
   ```
4. **קובצי הגדרות** (לא נכנסים ל־git):
   ```bash
   cp .env.example .env                        # דומיין + סיסמת מסד נתונים
   cp .env.production.example .env.production  # הגדרות האפליקציה
   ```
   - ב־`.env`: `DOMAIN`, ו־`POSTGRES_PASSWORD` ארוכה ואקראית.
   - ב־`.env.production`: `SITE_URL=https://הדומיין`, `DJANGO_SECRET_KEY` (יוצרים עם `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`), ו־`DATABASE_URL` עם **אותה** סיסמה.
   - Twilio ומייל – ראו "שירותים חיצוניים" למטה.
5. **הפעלה:**
   ```bash
   docker compose up -d --build
   ```
   בהפעלה הראשונה נבנה ה־image (כמה דקות), נוצרות הטבלאות, ו־Caddy מוציא תעודת HTTPS.
6. **יצירת המנהל הראשון:**
   ```bash
   docker compose exec web docker-entrypoint.sh createsuperuser
   ```
7. **בדיקה:** `https://הדומיין/api/health/` צריך להחזיר `{"status": "ok", "database": true}`. אחר כך נכנסים ל־`https://הדומיין` עם המנהל, ב"כניסה עם שם משתמש וסיסמה".

### עדכון גרסה
```bash
git pull
docker compose up -d --build
```
שינויים במסד הנתונים (migrations) רצים אוטומטית בעליית השרת.

### לוגים
```bash
docker compose logs -f web
```

---

### שרת חינמי ב־Oracle Cloud (Always Free)

השרת החינמי עם הכי הרבה זיכרון (2 מעבדים, 12GB, ללא הגבלת זמן). בהרשמה מבקשים כרטיס אשראי לאימות בלבד.

1. פותחים חשבון ב־[oracle.com/cloud/free](https://www.oracle.com/cloud/free/). את ה־**Home Region** בוחרים בזהירות (למשל Israel Central), כי אי אפשר לשנות אותו.
2. משדרגים את החשבון ל־**Pay As You Go** ומגדירים **Budget alert** של $1. בתוך המכסה החינמית זה עדיין חינם, וזה מונע מ־Oracle למחוק שרת "לא פעיל". מערכת גמ"ח שקטה עלולה להיחשב כזו.
3. **Compute → Instances → Create:**
   - Image: **Ubuntu 24.04**
   - Shape: **VM.Standard.A1.Flex**, עם 2 OCPU ו־12GB
   - מעלים מפתח SSH
   - אם מופיעה השגיאה "Out of host capacity", מנסים שוב מאוחר יותר או ב־Availability Domain אחר.
4. **כתובת IP קבועה:** בעמוד ה־Instance → Attached VNICs → IPv4 Addresses, הופכים את ה־Public IP ל־**Reserved**.
5. **פתיחת פורטים ברשת:** Virtual Cloud Network → Security List → Add Ingress Rules: `0.0.0.0/0`, TCP, פורטים **80** ו־**443**.
6. **פתיחת פורטים בתוך השרת** (בתמונות של Oracle הם חסומים כברירת מחדל):
   ```bash
   sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
   sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
   sudo netfilter-persistent save
   ```
7. **כתובת לאתר בחינם:** ב־[duckdns.org](https://www.duckdns.org) יוצרים תת־דומיין (למשל `gemach-yaakov.duckdns.org`) ומכניסים את ה־IP של השרת. את הכתובת הזו שמים ב־`DOMAIN` וב־`SITE_URL`.
8. ממשיכים מסעיף 2 למעלה (התקנת Docker).

---

## דרך ב' – Render.com

1. ב־Render: **New → Blueprint**, ובוחרים את המאגר. הקובץ `render.yaml` יוצר מסד נתונים, את האתר ומשימה יומית לתזכורות.
2. ממלאים את המשתנים שמסומנים לבחירה ידנית: `SITE_URL`, ופרטי Twilio ומייל. במשימת התזכורות מעתיקים את אותו `DJANGO_SECRET_KEY` שנוצר לאתר.
3. אחרי העלייה: **Shell** של השירות → `docker-entrypoint.sh createsuperuser`.

שימו לב: דיסק קבוע לטפסים החתומים דורש תוכנית בתשלום ב־Render. בלי דיסק, הטפסים יימחקו בכל עדכון. הגיבוי הלילי של docker compose לא רץ ב־Render; שם משתמשים בגיבוי המובנה של מסד הנתונים של Render.

---

## שירותים חיצוניים – לא חובה

המערכת עובדת **בלי SMS ובלי מייל, בחינם לגמרי**. במצב הזה:
- מסך הכניסה מציג רק **תעודת זהות (או שם משתמש) + סיסמה**.
- כשמנהל מוסיף לווה או נאמן, או מאפס סיסמה, מוצגת סיסמה זמנית, והמנהל מוסר אותה למשתמש בעצמו (בטלפון או על דף). בכניסה הראשונה המשתמש בוחר סיסמה חדשה.
- תזכורות תשלום לא נשלחות.

כשתרצו להוסיף, ממלאים את המשתנים ב־`.env.production` ומריצים `docker compose up -d`. הכניסה עם קוד וכפתורי השליחה יופיעו לבד, בלי שינוי קוד.

| שירות | מה הוא מוסיף | משתנים |
|---|---|---|
| Twilio | כניסה עם קוד ב־SMS, שליחת פרטי חשבון, תזכורות תשלום | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_SMS_FROM` |
| שרת מייל (SMTP) | כניסה עם קוד במייל, שליחת פרטי חשבון במייל | `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` |

`LOGIN_CODES=off` מכבה את הכניסה עם קוד גם כשהשירותים מוגדרים.

---

## גיבויים

- שירות `backup` מריץ כל לילה (בשעה `BACKUP_HOUR`, ברירת מחדל 02:00) גיבוי של מסד הנתונים ושל הטפסים החתומים ל־`/data/backups` בתוך ה־volume `app_data`. גיבויים בני יותר מ־`BACKUP_KEEP_DAYS` ימים נמחקים.
- גיבוי ידני עכשיו:
  ```bash
  docker compose exec web docker-entrypoint.sh backup
  ```
- **חובה להעתיק גיבויים גם מחוץ לשרת**, כי אם השרת נמחק, הגיבויים עליו נמחקים איתו:
  ```bash
  docker compose cp web:/data/backups ./backups-$(date +%F)
  ```

### שחזור
```bash
# מסד נתונים (מחליף את הקיים!)
docker compose cp db_2026-10-19_0200.dump web:/tmp/restore.dump
docker compose exec web sh -c 'pg_restore --clean --if-exists --no-owner -d "$DATABASE_URL" /tmp/restore.dump'

# טפסים חתומים
docker compose cp media_2026-10-19_0200.tar.gz web:/tmp/media.tar.gz
docker compose exec web tar -xzf /tmp/media.tar.gz -C /data/media
```
מומלץ לנסות שחזור פעם אחת לפני הפיילוט, על שרת בדיקה.

---

## רשימת בדיקה לפני הפיילוט

- [ ] `DJANGO_DEBUG=false` ו־`DJANGO_SECRET_KEY` ארוך ואקראי
- [ ] האתר עולה ב־HTTPS, ו־`/api/health/` מחזיר `ok`
- [ ] (רק אם הוגדר SMS / מייל) נשלח קוד כניסה לטלפון או למייל אמיתי
- [ ] לא הורצו `loaddata seed_data.json` ולא `seed_dev_users` (משתמשים עם סיסמאות ידועות)
- [ ] נוצר מנהל אמיתי, והסיסמה שלו לא נשלחה במייל או בצ'אט
- [ ] גיבוי לילי רץ, הועתק מחוץ לשרת, ונוסה שחזור
- [ ] (רשות) `DJANGO_ADMIN_URL` הועבר לכתובת לא צפויה

---

## פיתוח מקומי

לא השתנה: `backend` עם `runserver` ו־`frontend/client` עם `npm run dev`, ראו `README.md`. בפיתוח הממשק פונה ל־`http://127.0.0.1:8000/api` (לפי `frontend/client/.env`), ובבנייה לפרודקשן ל־`/api` (לפי `frontend/client/.env.production`).
