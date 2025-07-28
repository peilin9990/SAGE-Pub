let btnLeft = null;
let btnRight = null;

function createBtn(iconSvg, clickHandler) {
  const btn = document.createElement("button");
  btn.innerHTML = iconSvg;
  btn.style.position = "fixed";
  btn.style.zIndex = "9999";
  btn.style.background = "#fff";
  btn.style.border = "none";
  btn.style.padding = "12px";
  btn.style.borderRadius = "12px";
  btn.style.boxShadow = "0 2px 8px rgba(0,0,0,.10)";
  btn.style.cursor = "pointer";
  btn.style.transition = "background 0.2s";
  btn.addEventListener("mousedown", () => btn.style.background = "#eee");
  btn.addEventListener("mouseup", () => btn.style.background = "#fff");
  btn.addEventListener("mouseleave", () => btn.style.background = "#fff");
  btn.onclick = clickHandler;
  document.body.appendChild(btn);
  return btn;
}

// 右侧按钮用新的风格
function createBtnRight(iconSvg, clickHandler) {
  const btn = document.createElement("button");
  btn.setAttribute("aria-label", "隐藏/显示右侧目录");
  btn.style.position = "fixed";
  btn.style.zIndex = "9999";
  btn.style.background = "transparent";
  btn.style.border = "none";
  btn.style.padding = "6px";
  btn.style.borderRadius = "50%";
  btn.style.display = "flex";
  btn.style.alignItems = "center";
  btn.style.justifyContent = "center";
  btn.style.cursor = "pointer";
  btn.style.transition = "background 0.2s";
  btn.innerHTML = iconSvg;
  btn.onclick = clickHandler;

  // 悬浮和按下的高亮
  btn.addEventListener("mouseenter", () => {
    btn.style.background = "rgba(100,100,100,0.07)";
  });
  btn.addEventListener("mouseleave", () => {
    btn.style.background = "transparent";
  });
  btn.addEventListener("mousedown", () => {
    btn.style.background = "rgba(100,100,100,0.15)";
  });
  btn.addEventListener("mouseup", () => {
    btn.style.background = "rgba(100,100,100,0.07)";
  });

  document.body.appendChild(btn);
  return btn;
}

// 你可以自定义这里的按钮顶部安全距离
const SAFE_TOP = 150; // px

function updateBtnLeftPosition() {
  if (!btnLeft) return;
  const sidebar = document.querySelector(".md-sidebar--primary");
  const scrollwrap = document.querySelector(".md-sidebar--primary .md-sidebar__scrollwrap");
  if (sidebar && sidebar.style.display !== "none" && scrollwrap) {
    const rect = scrollwrap.getBoundingClientRect();
    btnLeft.style.left = `${rect.left - btnLeft.offsetWidth - 16}px`;
    btnLeft.style.top = `${rect.top-5}px`;
  } else {
    btnLeft.style.left = `130px`;
    btnLeft.style.top = `${SAFE_TOP+10}px`;
  }
}

function updateBtnRightPosition() {
  if (!btnRight) return;
  const sidebar = document.querySelector(".md-sidebar--secondary");
  const scrollwrap = document.querySelector(".md-sidebar--secondary .md-sidebar__scrollwrap");
  if (sidebar && sidebar.style.display !== "none" && scrollwrap) {
    const rect = scrollwrap.getBoundingClientRect();
    btnRight.style.left = `${rect.right + 16}px`;
    btnRight.style.top = `${rect.top}px`;
  } else {
    btnRight.style.left = `${window.innerWidth - btnRight.offsetWidth - 165}px`;
    btnRight.style.top = `${SAFE_TOP+15}px`;
  }
}

window.addEventListener("DOMContentLoaded", function () {
  if (window.innerWidth < 900) return;

  // 左侧按钮（原风格）
  btnLeft = createBtn(
    `<svg width="28" height="28" viewBox="0 0 28 28">
      <rect y="5" width="28" height="3" rx="1.5" fill="#333"/>
      <rect y="12.5" width="28" height="3" rx="1.5" fill="#333"/>
      <rect y="20" width="28" height="3" rx="1.5" fill="#333"/>
    </svg>`,
    function () {
      const sidebar = document.querySelector(".md-sidebar--primary");
      const main = document.querySelector(".md-main");
      if (sidebar && sidebar.style.display !== "none") {
        sidebar.style.display = "none";
        if (main) main.style.marginLeft = "0";
      } else if (sidebar) {
        sidebar.style.display = "";
        if (main) main.style.marginLeft = "";
      }
      setTimeout(updateBtnLeftPosition, 100);
    }
  );

  // 右侧按钮（新风格）
  btnRight = createBtnRight(
    `<svg width="20" height="20" viewBox="0 0 28 28">
      <rect y="5" width="28" height="3" rx="1.5" fill="#333"/>
      <rect y="12.5" width="28" height="3" rx="1.5" fill="#333"/>
      <rect y="20" width="28" height="3" rx="1.5" fill="#333"/>
    </svg>`,
    function () {
      const sidebar = document.querySelector(".md-sidebar--secondary");
      const main = document.querySelector(".md-main");
      if (sidebar && sidebar.style.display !== "none") {
        sidebar.style.display = "none";
        if (main) main.style.marginRight = "0";
      } else if (sidebar) {
        sidebar.style.display = "";
        if (main) main.style.marginRight = "";
      }
      setTimeout(updateBtnRightPosition, 100);
    }
  );

  function allUpdate() {
    updateBtnLeftPosition();
    updateBtnRightPosition();
  }

  allUpdate();
  window.addEventListener("resize", allUpdate);
  window.addEventListener("scroll", allUpdate);

  // 监听内容区变化（比如切换 Tab、窗口缩放导致布局刷新）
  const mainInner = document.querySelector(".md-main__inner");
  if (mainInner) {
    const observer = new MutationObserver(allUpdate);
    observer.observe(mainInner, {attributes: true, childList: true, subtree: true});
  }
});
