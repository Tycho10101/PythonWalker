function smoothFadeOut(element, duration) {
  return new Promise((resolve) => {
    let start = null;
    const initialOpacity = parseFloat(element.style.opacity) || 1;

    function animate(currentTime) {
      if (!start) start = currentTime;
      const progress = (currentTime - start) / duration;

      if (progress < 1) {
        element.style.opacity = initialOpacity * (1 - progress);
        requestAnimationFrame(animate);
      } else {
        element.style.opacity = 0;
        resolve();
      }
    }
    requestAnimationFrame(animate);
  });
}

function smoothFadeIn(element, duration) {
  return new Promise((resolve) => {
    let start = null;
    element.style.opacity = 0;

    function animate(currentTime) {
      if (!start) start = currentTime;
      const progress = (currentTime - start) / duration;

      if (progress < 1) {
        element.style.opacity = progress;
        requestAnimationFrame(animate);
      } else {
        element.style.opacity = 1;
        resolve();
      }
    }
    requestAnimationFrame(animate);
  });
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function openInfo(title, desc, id, user) {
  document.getElementById("game").innerHTML += `<div class="ui-modal fit-content" id="world-info-popup" style="opacity: 1;">
  <div class="container" style="transform: translate(0px);">
	<div class="title">${title}</div>
    <div class="subtitle">
      <span>By: </span>
      <span style="color: rgb(255, 255, 255);">${user}</span><br>
      <span>ID: </span>
      <span style="color: rgb(255, 255, 255);">${id}</span><br>
    </div>
    <div class="message">${desc}</div>
    <div class="minimap">
      <!-- to be implemented <img src=""> -->
    </div>
    <div class="buttons">
      <!--<div class="button default">Join World</div>-->
      <div class="button" onclick='deletePopup()'>Close</div>
    </div>
  </div>
</div>`;
}

async function getWorldInfo(id) {
  document.getElementById("friends-box").innerHTML =
    "<div class='header'><div class='title'>Loading...</div></div>";
  fetch(`/world-info/${id}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.text();
    })
    .then((data) => {
      document.getElementById("friends-box").innerHTML = data;
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
      document.getElementById("friends-box").innerHTML =
        "<div class='header'><div class='title'>Error loading data.</div></div>";
    });
}

function deletePopup() {
  document.getElementById("world-info-popup").remove()
}

document.addEventListener('DOMContentLoaded', async () => {
  const myElement = document.getElementsByClassName('background')[0];
  let bg_num = 1;

  if (myElement && myElement.firstElementChild && myElement.firstElementChild.tagName === 'IMG') {
    console.log('Element found:', myElement);
    const myImageElement = myElement.firstElementChild;

    myImageElement.src = "/assets/bg_" + bg_num + ".png";

    while (true) {
      await sleep(9000);

      await smoothFadeOut(myElement, 500);
	  
      bg_num++;
      if (bg_num > 4) {
        bg_num = 1;
      }
      myImageElement.src = "/assets/bg_" + bg_num + ".png";
	  
      void myImageElement.offsetWidth;
	  
      await new Promise(resolve => {
        if (myImageElement.complete && myImageElement.naturalHeight !== 0) {
          resolve();
        } else {
          myImageElement.onload = () => resolve();
          myImageElement.onerror = () => {
            console.error("Failed to load image:", myImageElement.src);
            resolve();
          };
        }
      });

      await smoothFadeIn(myElement, 500);
    }
  } else {
    console.error('Element with class "background" or its image child not found, or first child is not an IMG tag.');
  }
});