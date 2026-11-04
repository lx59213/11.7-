p='/Users/ttz/Project/neo/11.07-08实操课/中台版/_模块/modules.html'; s=open(p,encoding='utf-8').read()
for a,b in [('<div class="t4 ag"><b>专家</b>','<div class="t4 ag"><b>智能体</b>'),('<div class="t4 wf"><b>SOP</b>','<div class="t4 wf"><b>工作流</b>'),
            ('知识库、技能、专家、SOP','知识库、技能、智能体、工作流'),('要准备：专家、SOP、谁点头','要准备：工作流、谁点头'),('要准备：技能、知识库</p>','要准备：技能、知识库、智能体</p>'),
            ('<div class="dot">03</div><h3>专家</h3>','<div class="dot">03</div><h3>智能体</h3>'),('<div class="dot">04</div><h3>SOP</h3>','<div class="dot">04</div><h3>工作流</h3>')]:
    print(s.count(a)); s=s.replace(a,b)
open(p,'w',encoding='utf-8').write(s)
