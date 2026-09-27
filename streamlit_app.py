from pathlib import Path
import zipfile, textwrap, json

root = Path("/mnt/data/FoodConnect_HaulStyle")
src = root / "src"
src.mkdir(parents=True, exist_ok=True)

files = {
"package.json": r'''{
  "name": "foodconnect-modern-ui",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "framer-motion": "^12.0.0",
    "lucide-react": "^0.460.0",
    "vite": "^6.0.0",
    "typescript": "^5.7.2",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {}
}''',

"index.html": r'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#b9f44b" />
    <title>FoodConnect — Good Food. Less Waste. More Hope.</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>''',

"src/main.jsx": r'''import React from "react";
import { createRoot } from "react-dom/client";
import { motion } from "framer-motion";
import {
  ArrowRight, CheckCircle2, Clock3, HeartHandshake, Leaf,
  MapPin, Package, Phone, Recycle, ShieldCheck, Truck,
  UtensilsCrossed, Users, Zap
} from "lucide-react";
import "./styles.css";

const stats = [
  ["128+", "Donations rescued"],
  ["24+", "NGO partners"],
  ["96+", "Pickups accepted"],
  ["87+", "Completed rescues"],
];

const foodTypes = [
  ["🍱", "Cooked meals"], ["🥗", "Fresh food"], ["🍞", "Bakery items"],
  ["🥫", "Packaged food"], ["🍎", "Fruits & vegetables"], ["🎉", "Event surplus"],
  ["🏪", "Restaurant surplus"], ["🏠", "Household surplus"],
];

const steps = [
  ["01", "Donate surplus food", "Tell us what you have, how much there is, and when it can be collected."],
  ["02", "We find an NGO", "FoodConnect checks eligible nearby NGOs using location, capacity and availability."],
  ["03", "NGO accepts", "A verified NGO accepts the donation and receives a secure pickup token."],
  ["04", "Pickup confirmed", "The QR/token workflow confirms collection and updates the donation status."],
];

const ngos = [
  ["Helping Hands", "2.4 km away", "Verified NGO", "Vehicle available"],
  ["Feed the City", "3.1 km away", "Verified NGO", "Capacity available"],
  ["Seva Kitchen", "4.2 km away", "Verified NGO", "Vehicle available"],
];

function App() {
  return (
    <div className="app">
      <div className="topbar">
        <span>GOOD FOOD · LESS WASTE · MORE HOPE</span>
        <span className="topbar-right">Food rescue made simple</span>
      </div>

      <nav className="nav">
        <a className="brand" href="#home">
          <span className="brand-mark"><Leaf size={20} /></span>
          FOOD<span>CONNECT</span>
        </a>
        <div className="nav-links">
          <a href="#donate">Donate</a>
          <a href="#ngos">NGOs</a>
          <a href="#how">How it works</a>
          <a href="#impact">Impact</a>
        </div>
        <a className="nav-cta" href="#donate"><HeartHandshake size={17}/> Donate Food</a>
      </nav>

      <main>
        <section id="home" className="hero section">
          <div className="hero-copy">
            <motion.div initial={{opacity:0,y:15}} animate={{opacity:1,y:0}} className="eyebrow">
              <span className="dot"/> SURPLUS FOOD RESCUE PLATFORM
            </motion.div>
            <motion.h1
              initial="hidden" animate="show"
              variants={{show:{transition:{staggerChildren:.09}}}}
            >
              {["GOOD FOOD.", "LESS WASTE.", "MORE HOPE."].map((line,i)=>(
                <span className="hero-line" key={line}>
                  <motion.span variants={{hidden:{y:70,opacity:0},show:{y:0,opacity:1}}}>{line}</motion.span>
                </span>
              ))}
            </motion.h1>
            <p className="hero-text">
              Connect surplus food with verified NGOs. FoodConnect helps donors
              rescue usable food and makes pickup simple, traceable and reliable.
            </p>
            <div className="hero-actions">
              <a className="btn primary" href="#donate">Donate Food <ArrowRight size={18}/></a>
              <a className="btn secondary" href="#ngos">Explore NGOs <Users size={18}/></a>
            </div>
            <div className="trust-row">
              <span><ShieldCheck size={17}/> VERIFIED NGOS</span>
              <span><MapPin size={17}/> SMART MATCHING</span>
              <span><CheckCircle2 size={17}/> QR PICKUP</span>
            </div>
          </div>

          <motion.div
            className="hero-visual"
            initial={{opacity:0,scale:.96}} animate={{opacity:1,scale:1}}
            transition={{duration:1}}
          >
            <div className="impact-card">
              <div className="photo photo-before">
                <div className="photo-label">BEFORE</div>
                <div className="food-scene clutter">
                  <span>🍱</span><span>🥫</span><span>🍞</span><span>🥗</span><span>📦</span>
                </div>
              </div>
              <div className="photo photo-after">
                <div className="photo-label">AFTER</div>
                <div className="food-scene clean">
                  <Leaf size={62}/>
                  <strong>FOOD RESCUED</strong>
                  <small>Donated · Collected · Completed</small>
                </div>
              </div>
              <div className="diagonal-divider"/>
            </div>
            <div className="hero-badge"><Truck size={20}/><span><b>RESCUE IN MOTION</b><small>Donor → NGO → Pickup</small></span></div>
          </motion.div>
        </section>

        <section className="stats-strip">
          {stats.map(([value,label])=>(
            <div className="stat" key={label}><strong>{value}</strong><span>{label}</span></div>
          ))}
        </section>

        <section id="donate" className="section">
          <SectionHeading eyebrow="DONATE SURPLUS" title="If you have food to spare, we can help it reach people." />
          <div className="food-grid">
            {foodTypes.map(([icon,label])=>(
              <motion.div className="food-card" key={label} whileHover={{y:-4}}>
                <span className="food-icon">{icon}</span><span>{label}</span><ArrowRight size={16}/>
              </motion.div>
            ))}
          </div>
          <div className="note"><Zap size={18}/><span>Donors provide the food details. FoodConnect handles matching, status updates and pickup verification.</span></div>
        </section>

        <section id="ngos" className="section dark-section">
          <SectionHeading eyebrow="NGO DIRECTORY" title="Verified organisations ready to rescue food." light />
          <div className="ngo-grid">
            {ngos.map(([name,distance,verified,vehicle])=>(
              <motion.article className="ngo-card" key={name} whileHover={{y:-5}}>
                <div className="ngo-top"><div className="ngo-icon"><HeartHandshake size={23}/></div><span className="verified"><CheckCircle2 size={15}/> {verified}</span></div>
                <h3>{name}</h3>
                <div className="ngo-meta"><span><MapPin size={15}/>{distance}</span><span><Truck size={15}/>{vehicle}</span></div>
                <button className="text-button">View NGO <ArrowRight size={16}/></button>
              </motion.article>
            ))}
          </div>
        </section>

        <section id="how" className="section">
          <SectionHeading eyebrow="HOW IT WORKS" title="Four steps. One simple rescue." />
          <div className="steps">
            {steps.map(([num,title,text])=>(
              <motion.article className="step" key={num} whileHover={{y:-5}}>
                <div className="step-num">{num}</div>
                <div className="step-icon"><Package size={25}/></div>
                <h3>{title}</h3><p>{text}</p>
              </motion.article>
            ))}
          </div>
        </section>

        <section id="impact" className="section impact-section">
          <div className="impact-copy">
            <SectionHeading eyebrow="OUR IMPACT" title="Every completed pickup is a small win against food waste." />
            <p>FoodConnect creates a traceable journey from donation to NGO acceptance and pickup confirmation.</p>
            <div className="impact-points">
              <span><Recycle/> Reduce avoidable waste</span>
              <span><HeartHandshake/> Strengthen local NGO connections</span>
              <span><ShieldCheck/> Keep pickup verification clear</span>
            </div>
          </div>
          <div className="big-stat"><span>87+</span><strong>completed<br/>rescues</strong><small>based on current dashboard data</small></div>
        </section>

        <section className="section">
          <SectionHeading eyebrow="PICKUP WORKFLOW" title="From open donation to completed rescue." />
          <div className="timeline">
            {["OPEN", "ACCEPTED", "TOKEN VERIFIED", "COMPLETED"].map((s,i)=>(
              <div className="timeline-item" key={s}>
                <div className={`timeline-dot ${i===3 ? "active":""}`}>{i+1}</div>
                <div><strong>{s}</strong><span>{["Donation is available","NGO has accepted it","Pickup credentials checked","Collection is complete"][i]}</span></div>
              </div>
            ))}
          </div>
        </section>

        <section className="cta-section">
          <div>
            <span className="eyebrow dark-eyebrow">READY TO RESCUE FOOD?</span>
            <h2>DONATE FOOD.<br/>CREATE IMPACT.</h2>
            <p>Use FoodConnect to turn surplus into a meaningful community connection.</p>
          </div>
          <a className="dark-btn" href="#donate">Start a Donation <ArrowRight size={19}/></a>
        </section>
      </main>

      <footer className="footer">
        <div className="brand"><span className="brand-mark"><Leaf size={20}/></span>FOOD<span>CONNECT</span></div>
        <p>Good Food. Less Waste. More Hope.</p>
        <div className="footer-links"><a href="#donate">Donate</a><a href="#ngos">NGOs</a><a href="#how">How it works</a><a href="#impact">Impact</a></div>
        <small>© 2026 FoodConnect · Final Year Project</small>
      </footer>

      <a className="mobile-donate" href="#donate"><HeartHandshake size={18}/> DONATE FOOD</a>
    </div>
  );
}

function SectionHeading({eyebrow,title,light=false}) {
  return (
    <div className={`section-heading ${light ? "light" : ""}`}>
      <span className="eyebrow">{eyebrow}</span>
      <h2>{title}</h2>
      <div className="underline"/>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
''',

"src/styles.css": r'''@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&display=swap');

:root{
  --bg:#101a17;--fg:#f3f7f2;--lime:#b9f44b;--lime2:#d3ff72;
  --muted:#9ca9a2;--border:#26332e;--card:#17221e;--white:#fff;
}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--fg);font-family:Archivo,Arial,sans-serif;font-weight:500}a{text-decoration:none;color:inherit}
.app{min-height:100vh}.topbar{height:40px;background:var(--lime);color:#101a17;display:flex;align-items:center;justify-content:space-between;padding:0 32px;font-size:11px;font-weight:900;letter-spacing:.08em}.nav{height:78px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 5vw;position:sticky;top:0;background:rgba(16,26,23,.94);backdrop-filter:blur(12px);z-index:20}.brand{display:flex;align-items:center;gap:8px;font-weight:900;font-size:20px;letter-spacing:-.04em}.brand>span:last-child,.brand span+span{color:var(--lime)}.brand-mark{width:34px;height:34px;border-radius:10px;background:var(--lime);color:var(--bg);display:grid;place-items:center}.nav-links{display:flex;gap:28px;font-size:13px}.nav-links a{color:#c8d0cc}.nav-links a:hover{color:var(--lime)}.nav-cta,.btn.primary{background:var(--lime);color:var(--bg);font-weight:900;border-radius:9px;padding:13px 17px;display:inline-flex;align-items:center;gap:8px}.nav-cta{font-size:12px}.section{max-width:1280px;margin:auto;padding:100px 5vw}.hero{min-height:690px;display:grid;grid-template-columns:1.03fr .97fr;align-items:center;gap:6vw;padding-top:75px}.eyebrow{font-size:11px;letter-spacing:.12em;font-weight:900;color:var(--lime);display:inline-flex;align-items:center;gap:8px}.dot{width:7px;height:7px;border-radius:50%;background:var(--lime)}h1{font-size:clamp(52px,8vw,118px);line-height:.9;letter-spacing:-.055em;margin:20px 0 25px;font-weight:900}.hero-line{display:block;overflow:hidden}.hero-text{font-size:17px;line-height:1.65;color:#b6c0ba;max-width:650px}.hero-actions{display:flex;gap:12px;margin:30px 0}.btn{min-height:48px;padding:13px 18px;border-radius:9px;display:inline-flex;align-items:center;gap:9px;font-weight:900;font-size:13px}.btn.secondary{border:1px solid #3a4742;color:var(--fg)}.btn:hover{transform:translateY(-2px)}.btn.primary:hover{background:var(--lime2)}.trust-row{display:flex;gap:20px;flex-wrap:wrap;font-size:10px;font-weight:900;letter-spacing:.08em;color:#87948d}.trust-row span{display:flex;gap:6px;align-items:center}.trust-row svg{color:var(--lime)}
.hero-visual{position:relative}.impact-card{position:relative;aspect-ratio:4/3;border-radius:22px;overflow:hidden;border:1px solid #36423d;box-shadow:0 25px 70px #0008}.photo{position:absolute;inset:0}.photo-before{background:linear-gradient(135deg,#8b765e,#413c31)}.photo-after{background:linear-gradient(135deg,#e7eee3,#8ca88b);clip-path:polygon(100% 0,100% 100%,22% 100%)}.food-scene{height:100%;display:flex;align-items:center;justify-content:center;gap:25px;font-size:55px}.clutter{transform:rotate(-8deg);filter:saturate(.8)}.clean{flex-direction:column;gap:7px;color:#19301f}.clean strong{font-size:22px}.clean small{font-size:10px}.photo-label{position:absolute;z-index:4;font-size:12px;font-weight:900;letter-spacing:.12em;color:var(--lime);background:#101a17dd;padding:8px 10px;border-radius:5px}.photo-before .photo-label{left:18px;bottom:18px}.photo-after .photo-label{right:18px;top:18px}.diagonal-divider{position:absolute;inset:0;background:linear-gradient(139deg,transparent 0%,transparent 49.7%,var(--lime) 50%,var(--lime) 50.3%,transparent 50.4%);pointer-events:none}.hero-badge{position:absolute;right:-22px;bottom:-22px;background:var(--lime);color:var(--bg);padding:14px 18px;border-radius:13px;display:flex;gap:10px;align-items:center;box-shadow:0 15px 35px #0007}.hero-badge span{display:flex;flex-direction:column;gap:3px}.hero-badge b{font-size:11px}.hero-badge small{font-size:10px}.stats-strip{border-block:1px solid var(--border);display:grid;grid-template-columns:repeat(4,1fr);max-width:1280px;margin:auto}.stat{padding:28px 5vw;border-right:1px solid var(--border)}.stat:last-child{border:0}.stat strong{display:block;font-size:36px;font-weight:900;color:var(--lime)}.stat span{font-size:11px;color:#8e9a94;text-transform:uppercase;letter-spacing:.08em}
.section-heading{max-width:800px;margin-bottom:45px;position:relative}.section-heading h2{font-size:clamp(34px,4.5vw,64px);line-height:.96;letter-spacing:-.045em;margin:15px 0 18px;font-weight:900}.underline{width:85px;height:5px;background:var(--lime);transform-origin:left}.section-heading.light h2{color:var(--fg)}.food-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.food-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px;display:flex;align-items:center;gap:12px;font-weight:700;font-size:13px;transition:.2s}.food-card:hover{border-color:#526049}.food-card>svg{margin-left:auto;color:#6e7d75}.food-icon{font-size:25px}.note{margin-top:18px;border:1px solid var(--border);padding:17px;border-radius:10px;color:#aab5af;font-size:13px;display:flex;gap:10px;align-items:center}.note svg{color:var(--lime);flex:none}
.dark-section{max-width:none;background:#0c1412}.dark-section>.section-heading,.dark-section>.ngo-grid{max-width:1180px;margin-left:auto;margin-right:auto}.ngo-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.ngo-card{background:var(--card);border:1px solid var(--border);border-radius:15px;padding:25px}.ngo-top{display:flex;justify-content:space-between}.ngo-icon{width:48px;height:48px;border-radius:12px;background:#24352e;display:grid;place-items:center;color:var(--lime)}.verified{font-size:9px;letter-spacing:.08em;color:var(--lime);display:flex;align-items:center;gap:5px}.ngo-card h3{font-size:25px;margin:24px 0 18px}.ngo-meta{display:flex;flex-direction:column;gap:9px;color:#99a59f;font-size:12px}.ngo-meta span{display:flex;gap:7px;align-items:center}.ngo-meta svg{color:var(--lime)}.text-button{margin-top:25px;background:none;border:0;color:var(--lime);font:700 12px Archivo;display:flex;gap:7px;align-items:center;padding:0;cursor:pointer}
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.step{border-top:2px solid var(--border);padding-top:20px}.step-num{font-size:14px;color:var(--lime);font-weight:900}.step-icon{margin:22px 0;width:48px;height:48px;border:1px solid var(--border);border-radius:10px;display:grid;place-items:center;color:var(--lime)}.step h3{font-size:20px;margin:0 0 10px}.step p{color:#929e98;font-size:13px;line-height:1.6}
.impact-section{display:grid;grid-template-columns:1.2fr .8fr;gap:8vw;align-items:center}.impact-copy>p{max-width:650px;color:#9ba7a1;line-height:1.7}.impact-points{display:grid;gap:12px;margin-top:25px}.impact-points span{display:flex;gap:10px;align-items:center;font-size:13px}.impact-points svg{color:var(--lime);width:19px}.big-stat{border:1px solid var(--border);border-radius:22px;padding:45px;background:var(--card);display:flex;flex-direction:column}.big-stat span{font-size:clamp(70px,9vw,125px);line-height:.8;color:var(--lime);font-weight:900;letter-spacing:-.06em}.big-stat strong{font-size:28px;line-height:1;margin-top:25px}.big-stat small{color:#7f8d85;margin-top:20px}
.timeline{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--border)}.timeline-item{padding:28px 20px 0 0;display:flex;gap:13px;position:relative}.timeline-dot{width:32px;height:32px;border:1px solid #3c4b44;border-radius:50%;display:grid;place-items:center;color:#829087;font-size:11px;font-weight:900;flex:none}.timeline-dot.active{background:var(--lime);color:var(--bg);border-color:var(--lime)}.timeline-item div:last-child{display:flex;flex-direction:column;gap:6px}.timeline-item strong{font-size:12px}.timeline-item span{font-size:11px;color:#7f8d85;line-height:1.5}
.cta-section{background:var(--lime);color:var(--bg);padding:80px max(5vw,30px);display:flex;align-items:center;justify-content:space-between;gap:40px}.dark-eyebrow{color:var(--bg);opacity:.7}.cta-section h2{font-size:clamp(42px,6vw,82px);line-height:.9;letter-spacing:-.05em;margin:14px 0}.cta-section p{max-width:620px;font-size:15px}.dark-btn{background:var(--bg);color:var(--fg);padding:16px 20px;border-radius:10px;display:inline-flex;align-items:center;gap:10px;font-weight:900;font-size:13px;white-space:nowrap}.footer{padding:50px 5vw;display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:30px;align-items:start}.footer p,.footer small{color:#7e8b84;font-size:12px}.footer-links{display:flex;flex-direction:column;gap:10px;font-size:12px;color:#aab4af}.mobile-donate{display:none}
@media(max-width:900px){.nav-links{display:none}.hero{grid-template-columns:1fr;padding-top:55px}.hero-visual{order:-1}.hero-badge{right:10px}.food-grid{grid-template-columns:repeat(2,1fr)}.steps{grid-template-columns:repeat(2,1fr)}.ngo-grid{grid-template-columns:1fr}.impact-section{grid-template-columns:1fr}.timeline{grid-template-columns:repeat(2,1fr);gap:20px}.footer{grid-template-columns:1fr 1fr}}
@media(max-width:600px){.topbar{padding:0 15px;font-size:8px}.topbar-right{display:none}.nav{height:68px;padding:0 15px}.nav-cta{padding:10px}.nav-cta{font-size:0}.nav-cta:after{content:"DONATE";font-size:10px}.section{padding:70px 20px}.hero{padding-top:35px}.hero-text{font-size:15px}.hero-actions{flex-direction:column}.btn{justify-content:center}.trust-row{gap:10px;flex-direction:column}.impact-card{border-radius:15px}.hero-badge{position:relative;right:auto;bottom:auto;margin-top:12px}.stats-strip{grid-template-columns:repeat(2,1fr)}.stat{padding:20px;border-bottom:1px solid var(--border)}.stat:nth-child(2){border-right:0}.food-grid{grid-template-columns:repeat(2,1fr)}.food-card{padding:13px;font-size:11px}.steps{grid-template-columns:1fr}.timeline{grid-template-columns:1fr}.cta-section{padding:65px 20px;display:block}.dark-btn{margin-top:25px}.footer{grid-template-columns:1fr;padding-bottom:90px}.mobile-donate{display:flex;position:fixed;bottom:12px;left:12px;right:12px;z-index:50;background:var(--lime);color:var(--bg);justify-content:center;align-items:center;gap:8px;padding:15px;border-radius:10px;font-size:12px;font-weight:900;box-shadow:0 10px 30px #0008}}
'''
}

for rel, content in files.items():
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

zip_path = Path("/mnt/data/FoodConnect_HaulStyle_React.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p in root.rglob("*"):
        if p.is_file():
            z.write(p, p.relative_to(root.parent))

print(f"Created: {zip_path}")
print("This is a React/Vite visual frontend prototype based on the supplied Haul Co. design language, adapted for FoodConnect.")

