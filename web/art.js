// Original procedural artwork. Logical world coordinates are 1200 x 760.
const palettes = {
  snoopy: {sky:'#d7e7d9',water:'#94bbb0',shore:'#d9d4a8',grass:'#b4cc9e',path:'#e5d7ac',tree:'#6e9875',roof:'#b96f51',text:'#4d7256'},
  penguin: {sky:'#d7dfed',water:'#95adc5',shore:'#b9cbd5',grass:'#e4edf0',path:'#cedae4',tree:'#8da9b1',roof:'#748eaa',text:'#667e98'}
};
function ellipse(c,x,y,rx,ry,color){c.fillStyle=color;c.beginPath();c.ellipse(x,y,rx,ry,0,0,Math.PI*2);c.fill();}
function round(c,x,y,w,h,r,color){c.fillStyle=color;c.beginPath();c.roundRect(x,y,w,h,r);c.fill();}
function line(c,points,color,width){c.strokeStyle=color;c.lineWidth=width;c.lineCap='round';c.lineJoin='round';c.beginPath();points.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.stroke();}
function label(c,text,x,y,p){c.font='12px Segoe UI';const w=c.measureText(text).width+24;round(c,x-w/2,y-13,w,25,12,'#fffcf1d9');c.fillStyle=p.text;c.textAlign='center';c.fillText(text,x,y+4);}
function tree(c,x,y,p,s=1,snow=false){c.save();c.translate(x,y);c.scale(s,s);ellipse(c,0,6,38,13,'#56725716');round(c,-7,-45,14,51,5,'#9c8460');ellipse(c,0,-63,39,40,p.tree);ellipse(c,-23,-42,28,25,p.tree);ellipse(c,23,-44,28,26,p.tree);ellipse(c,-9,-77,27,23,snow?'#dfeaf0':'#8ead7e');if(snow){ellipse(c,0,-87,29,11,'#eff4f4');ellipse(c,-27,-53,20,8,'#eff4f4');}c.restore();}
function house(c,x,y,p,s=1){c.save();c.translate(x,y);c.scale(s,s);ellipse(c,0,10,78,20,'#4a645218');round(c,-62,-77,124,85,8,'#f4e6c6');round(c,-63,-19,126,27,5,'#e1c89d');c.fillStyle=p.roof;c.beginPath();c.moveTo(-80,-71);c.lineTo(0,-139);c.lineTo(81,-71);c.closePath();c.fill();line(c,[[-75,-72],[0,-132],[76,-72]],'#fff9df55',4);round(c,-15,-40,30,48,14,'#8c9472');round(c,-48,-52,22,25,5,'#9db9ac');round(c,27,-52,22,25,5,'#9db9ac');line(c,[[-37,-51],[-37,-28]],'#fef5db',3);line(c,[[38,-51],[38,-28]],'#fef5db',3);round(c,35,-135,15,39,2,'#c4a788');c.restore();}
export function character(c,x,y,species,scale=1,scarf='#ca8e6d',bounce=0){c.save();c.translate(x,y+bounce);c.scale(scale,scale);ellipse(c,0,17,20,7,'#49665524');if(species==='penguin'){ellipse(c,0,-7,18,27,'#526b79');ellipse(c,0,0,12,19,'#fff6dc');ellipse(c,0,-28,17,16,'#526b79');ellipse(c,0,-25,12,10,'#fff8e6');ellipse(c,-8,19,9,4,'#d7a45d');ellipse(c,8,19,9,4,'#d7a45d');c.fillStyle='#d5a15e';c.beginPath();c.moveTo(-4,-25);c.lineTo(0,-19);c.lineTo(5,-25);c.fill();ellipse(c,-19,-3,5,14,'#526b79');ellipse(c,19,-3,5,14,'#526b79');}else{ellipse(c,0,0,18,21,'#f5e8cb');ellipse(c,0,-27,23,19,'#fff2d7');ellipse(c,-21,-19,8,19,'#9e7960');ellipse(c,21,-19,8,19,'#9e7960');ellipse(c,0,-20,11,8,'#fff9e7');ellipse(c,0,-23,5,3,'#52614c');ellipse(c,-9,18,8,5,'#e0cfab');ellipse(c,10,18,8,5,'#e0cfab');}ellipse(c,-7,-31,2,2.5,'#354e4d');ellipse(c,7,-31,2,2.5,'#354e4d');round(c,-16,-13,32,7,3,scarf);round(c,8,-9,8,16,2,scarf);c.restore();}
export function render(c,state,visual,t){const p=palettes[state?.player.world||'snoopy'],snow=state?.player.world==='penguin';c.clearRect(0,0,1200,760);c.fillStyle=p.sky;c.fillRect(0,0,1200,760);
  // Quiet sky, drifting clouds, and a water horizon.
  for(let i=0;i<6;i++){const x=((i*237+t*2)%1450)-120,y=65+(i%3)*45;ellipse(c,x,y,60,13,'#fffdf543');ellipse(c,x+35,y-10,37,19,'#fffdf543');}
  if(snow){c.strokeStyle='#a3c3c934';c.lineWidth=28;c.beginPath();c.moveTo(700,30);c.bezierCurveTo(860,130,960,-50,1200,75);c.stroke();}
  c.fillStyle=p.water;c.fillRect(0,355,1200,405);
  for(let i=0;i<26;i++){const x=(i*173+24)%1200,y=385+(i*31)%360;line(c,[[x,y],[x+20+Math.sin(t+i)*4,y]],'#ecf4e930',2);}
  // A soft floating island with a visible sandy rim.
  ellipse(c,603,568,520,130,'#4e79762a');ellipse(c,604,453,535,218,p.shore);ellipse(c,601,430,530,219,p.grass);
  ellipse(c,985,276,100,57,p.grass);ellipse(c,176,351,100,100,p.grass);
  // Paths connect destinations; these are walkable open towns, not mazes.
  line(c,[[180,470],[420,420],[550,390],[810,440],[1020,390]],p.path,49);
  line(c,[[550,390],[540,250]],p.path,37);line(c,[[420,420],[320,535]],p.path,33);line(c,[[810,440],[840,520]],p.path,31);line(c,[[720,410],[750,305]],p.path,25);
  // Small deterministic patches and flowers.
  for(let i=0;i<115;i++){const x=140+(i*83)%920,y=245+(i*47)%360;if(Math.hypot((x-600)/2,y-430)>210)continue;ellipse(c,x,y,2.5,1.4,snow?'#bdced75c':'#94b58365');if(i%7===0){ellipse(c,x,y-4,3,3,snow?'#f9faff':'#f5e9b1');ellipse(c,x+4,y-3,2,2,snow?'#d8cfe9':'#e4ac94');}}
  // Island scenery.
  house(c,540,262,p,1.05);label(c,'The little workshop',540,293,p);house(c,172,470,p,.65);label(c,'Harbor cottage',174,507,p);
  tree(c,135,290,p,.8,snow);tree(c,338,250,p,.65,snow);tree(c,926,273,p,.8,snow);tree(c,970,492,p,.7,snow);
  // Resource grove and its stack of driftwood.
  tree(c,240,300,p,1.05,snow);for(let i=0;i<3;i++){round(c,213+i*9,294-i*5,43,10,5,'#ac805a');ellipse(c,214+i*9,299-i*5,5,5,'#d5b286');}label(c,'Driftwood grove',240,342,p);
  const node=state?.content.worlds[state.player.world].nodes[1];const nx=node?.x||760;
  if(snow){for(let i=0;i<4;i++){c.fillStyle=['#bddce7','#a0c9dc','#d4e8f0'][i%3];c.beginPath();c.moveTo(nx-36+i*20,312);c.lineTo(nx-32+i*20,261-(i%2)*22);c.lineTo(nx-17+i*20,246-(i%2)*22);c.lineTo(nx-6+i*20,303);c.closePath();c.fill();line(c,[[nx-24+i*20,263],[nx-17+i*20,294]],'#f2faffaa',2);}label(c,'Moon ice ridge',nx,344,p);}else{for(let i=0;i<5;i++)ellipse(c,nx-33+i*16,295-(i%2)*14,24,23,'#789d6b');for(let i=0;i<15;i++)ellipse(c,nx-38+(i*17)%78,278+(i*13)%34,3.5,4,'#d78479');label(c,'Sunberry patch',nx,342,p);}
  // Pond, a dock, a post hut and a tiny ferry arch.
  ellipse(c,320,548,109,49,snow?'#b2cadb':'#82b3a7');ellipse(c,320,545,101,41,snow?'#91b1c9':'#94c3b1');for(let i=0;i<4;i++){round(c,387,524+i*10,63,9,1,'#c9a97f');}for(let i=0;i<3;i++)ellipse(c,277+i*36,543+Math.sin(t+i)*4,8,2,'#f6fcf657');label(c,'Silverfin pond',320,611,p);
  house(c,840,525,p,.55);round(c,872,492,18,33,4,'#c88d78');round(c,870,493,22,13,5,'#c88d78');label(c,'Neighborhood post',840,568,p);
  // The sky ferry provides travel between both islands.
  ellipse(c,1050,397,62,28,'#d1c3a1');round(c,1017,312,12,83,4,'#baac8c');round(c,1072,312,12,83,4,'#baac8c');c.strokeStyle='#c6b995';c.lineWidth=13;c.beginPath();c.arc(1050,319,28,Math.PI,0);c.stroke();ellipse(c,1050,352,21,33,snow?'#abc8bb':'#b4c9dc');for(let i=0;i<3;i++)ellipse(c,1040+i*10,350+Math.sin(t*2+i)*10,2,2,'#fff9da');label(c,snow?'Ferry to Snoopyland':'Ferry to Penguinland',1030,442,p);
  // Welcome neighbor (not a bot player).
  character(c,655,438,snow?'penguin':'dog',1,'#dfb96e',Math.sin(t*2)*1.2);label(c,snow?'Pip · town host':'Mabel · town host',655,483,p);
  // A few strings of lights make the harbor feel lived in.
  line(c,[[405,197],[470,213],[550,222],[625,211],[693,190]],'#829272',1.5);for(let i=0;i<9;i++){const x=416+i*32,y=205+Math.sin(i/8*Math.PI)*18;round(c,x,y,6,9,3,snow?'#f1deab':'#f0d7a2');}
  if(visual.target){c.strokeStyle='#fffcef99';c.lineWidth=2;c.beginPath();c.ellipse(visual.target.x,visual.target.y+13,13+Math.sin(t*5)*2,5,0,0,Math.PI*2);c.stroke();}
  if(state){for(const friend of state.players.filter(f=>f.world===state.player.world)){character(c,friend.x,friend.y,friend.species,.95,'#9c9fc2');label(c,friend.name,friend.x,friend.y+38,p);}const me=state.player;character(c,visual.x,visual.y,me.species,1.12,'#b86d53',visual.walking?Math.sin(t*14)*2:Math.sin(t*2)*.7);label(c,me.name+' · you',visual.x,visual.y+42,p);}
  if(snow){for(let i=0;i<35;i++){ellipse(c,(i*97+t*5)%1200,(i*71+t*12)%700,1.5,1.5,'#ffffff79');}}
}
