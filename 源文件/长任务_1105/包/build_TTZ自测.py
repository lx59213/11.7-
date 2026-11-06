#!/usr/bin/env python3
"""TTZ 自己在 WorkBuddy 里把技能、智能体两块跑一遍用的测试单：每步要复制的那段 + 周晓的答法。
输出 学员资料_发放包/TTZ自测/测试单.html。包改了重跑一次。"""
import glob, html, os

ROOT = "/Users/ttz/Project/neo/11.07-08实操课"
PKG = ROOT + "/中台版/给codex/1105夜/交付/包_v12"
OUT = ROOT + "/学员资料_发放包/TTZ自测/测试单.html"
VAULT = ROOT + "/学员资料_发放包/TTZ自测/我的公司AI"

ANS = {
 ("技能", 1): ["它列的候选里有「回询盘第一封回信」：猜对就回「对」，没猜它就回「回询盘第一封回信」。",
              "问新人最常错在哪：「交期写得含糊。去年 11 月小林给荷兰一家回 before Christmas，1 月 8 号才到鹿特丹，扣了 5% 货款。」"],
 ("技能", 2): ["问赶不上的日期为什么放第一句：客户最关心能不能赶上，绕到最后才说像糊弄。去年 11 月小林给荷兰一家回 before Christmas，1 月 8 号才到鹿特丹，扣了 5% 货款，第二单也没了。",
              "问三档价为什么全报：很多人看到下一档便宜会往上加。今年 8 月波兰的 Marek 问 600 台，看到 1,000 台那档 11.90，改下了 1,000 台。",
              "问 logo 为什么写加价和起订量：2025 年 6 月一封只写了 yes we can，客户下单后才说每台加 0.50，客户不认，400 美元我们自己出了。",
              "问证书：只说手上有的。2024 年有人发了过期证书，客户清关被扣两周。",
              "问上一回你自己怎么做的：「上周回波兰 Marek：先说 12 月 10 日赶不上、最早能到哪天，再报三档价，logo 写加价和起订量，证书只附 CE。」",
              "想测「只回对」：随便哪问只回「对」，看它追不追。"],
 ("技能", 3): ["只看对比页两份正文，哪份你敢直接发给客户就回哪份（「甲」或「乙」），别猜哪份用了技能。",
              "问好在哪：说一处真觉得好的。想测没过：回不用技能那份，或回「差不多」，看它改技能重做。"],
 ("技能", 4): ["问就改这句吗：「对」。", "甲乙：照你真实判断回。"],
 ("技能", 5): ["问谁用谁改：「我和小林回询盘都用；我负责改，小林发现回错了截图发我。」",
              "问现在装吗：「先不装」（测试别装进你自己的 WorkBuddy）。"],
 ("智能体", 1): ["「行。它叫询盘初回员，服务我和小林；客户要贴 logo 的，配一张贴好 logo 的效果图。」"],
 ("智能体", 2): ["问停下等拍板的几种：「再加：logo 要两种以上颜色或印在底座以外。价格、交期、付款交老陈，证书交阿梅。」",
                "问 logo 为什么只印底座：水箱透明印不上，只有底座正面那一条，单色，最大 40×15 毫米。2025 年 7 月给波兰的图印在水箱上，付了定金才知道做不出，退了定金丢了单。",
                "问上一回你自己怎么做的：「上周给迪拜那单：先查插头是英规，效果图 logo 放底座，价格交老陈定了才发。」"],
 ("智能体", 3): ["请示单：每条真看，建议对就「都照建议」，不对就驳回改掉。", "甲乙：只看哪份你敢直接交出去。问好在哪：说一处。"],
 ("智能体", 4): ["问几点：「行」。它说建不了定时：「建好了」。请示单：照真实判断。",
                "问放心吗：照真实判断；不放心就说哪里。",
                "注意：WorkBuddy 能建定时的话会真建一个每天 9 点的任务，测完去「定时任务」里删掉。"],
 ("智能体", 5): ["问就改这句吗：「对」。", "甲乙：照真实判断。",
                "问谁用、谁拍板：「我和小林用；价格付款老陈拍，证书阿梅拍，其余我拍。」"],
 ("智能体", 6): ["问这三段现在谁在做：「都是我和小林。叫回信员、效果图员、把关员。」",
                "问哪一棒最容易出事：「效果图员交给把关员那一棒。今年 3 月给迪拜的图画了欧规插头，没人看出来，客户差点转单。」"],
 ("智能体", 7): ["请示单：照真实判断。", "问哪件不放心：照真实判断，说哪件、哪里。"],
 ("智能体", 8): ["问就改这句吗：「对」。", "甲乙：照真实判断。"],
 ("智能体", 9): ["问这类放行行吗：「行」。问谁用谁拍板：「还是这样」。"],
}

ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>')


def steps(d):
    out = []
    for f in sorted(glob.glob(f"{PKG}/{d}/提示词/[0-9]_*.md"), key=lambda p: int(os.path.basename(p).split("_")[0])):
        meta, body = open(f, encoding="utf-8").read().split("\n\n", 1)
        title = meta.splitlines()[0].lstrip("# ").strip()
        out.append((int(os.path.basename(f).split("_")[0]), title, body.strip()))
    return out


def box(t):
    return (f'<div class="box"><button onclick="cp(this)">{ICON}</button><pre>{html.escape(t)}</pre></div>')


def main():
    s = ['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>测试单</title><style>'
         'body{margin:0;font:16px/1.8 "PingFang SC",sans-serif;color:#2c2c2c;background:#fff}main{max-width:760px;margin:0 auto;padding:40px 24px 80px}'
         'h1{font-size:26px;margin:0 0 8px}h2{font-size:19px;margin:36px 0 8px;padding-top:20px;border-top:1px solid #e8e4dc}'
         '.prep{background:#faf7f2;border-left:3px solid #b35c37;padding:10px 16px;border-radius:0 8px 8px 0}.prep li{margin:4px 0}'
         '.ans{background:#eef5ef;border-radius:8px;padding:8px 14px;margin:8px 0}.ans b{color:#2e6b3a}.ans li{margin:3px 0}'
         '.box{position:relative;margin:10px 0}pre{margin:0;background:#f6f5f2;border:1px solid #e8e4dc;border-radius:10px;padding:16px 52px 16px 18px;white-space:pre-wrap;word-break:break-word;font:13px/1.7 "SF Mono",Menlo,"PingFang SC",monospace}'
         '.box button{position:absolute;top:10px;right:10px;width:32px;height:32px;border:1px solid #e8e4dc;border-radius:8px;background:#fff;cursor:pointer;color:#6b6b6b}'
         '.box button svg{width:16px;height:16px}.box button.ok{color:#2e7d32;border-color:#2e7d32}code{background:#f6f5f2;padding:0 4px;border-radius:3px}'
         'p,li{text-wrap:pretty}</style></head><body><main>',
         '<h1>测试单：技能、智能体两块跑一遍</h1>',
         '<div class="prep"><b>开跑前</b><ol>'
         f'<li>WorkBuddy 新建任务，工作文件夹选 <code>{html.escape(VAULT)}</code>（周晓的示例知识库，小，跑得快；别用自己的大库）。</li>'
         '<li>技能第 1 步：把上一层 学员资料_发放包/ 里的 <code>2_技能.zip</code> 整个拖进对话，再复制下面第 1 步，一起发。之后每步复制一段。</li>'
         '<li>AI 问的照绿框答；绿框写「照真实判断」的，你自己看了再答。挑甲乙只看哪份敢直接发。</li>'
         '<li>看板每一步的样子我在后台自动存，你不用截图。跑完说一声，我把十四个版本做成讲师版成果看板。</li></ol></div>']
    for d, pack in [("2_技能", "技能"), ("3_智能体", "智能体")]:
        if pack == "智能体":
            s.append('<h2 style="border-top:3px solid #b35c37">智能体：把 <code>3_智能体.zip</code> 拖进同一个对话，再复制第 1 步一起发</h2>')
        for k, title, body in steps(d):
            s.append(f'<h2>{pack} · {html.escape(title)}</h2>')
            a = ANS.get((pack, k), [])
            if a:
                s.append('<div class="ans"><b>AI 问到这样答</b><ul>' + "".join(f"<li>{html.escape(x)}</li>" for x in a) + '</ul></div>')
            s.append(box(body))
    s.append('<script>function cp(b){var t=b.parentNode.querySelector("pre").textContent;'
             'function ok(){b.classList.add("ok");setTimeout(function(){b.classList.remove("ok")},1500)}'
             'if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(ok)}else{var a=document.createElement("textarea");a.value=t;document.body.appendChild(a);a.select();document.execCommand("copy");a.remove();ok()}}</script></main></body></html>')
    open(OUT, "w", encoding="utf-8").write("".join(s))
    print("ok", OUT)


if __name__ == "__main__":
    main()
