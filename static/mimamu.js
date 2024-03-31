let MiMaMu = (function () {
    const now = Date.now();
    const today = Math.floor(now / 86400000);
    const tomorrow = new Date();
    tomorrow.setUTCHours(24, 0, 0, 0);
    var daily, guesses;
    var allGuesses;

    var initialDay;
    var puzzleNumber;
    function getCookie(cookieName) {
      let cookie = {};
      document.cookie.split(';').forEach(function(el) {
        let [key,value] = el.split('=');
        cookie[key.trim()] = value;
      })
      return cookie[cookieName];
    }
    const lang = getCookie("lang") || "en";

    function clearCache() {
      localStorage.removeItem(getCacheKey("mmm_allGuesses"));
      localStorage.removeItem(getCacheKey("mmm_guesses"));
      localStorage.removeItem(getCacheKey("winState"));
      localStorage.removeItem(getCacheKey("daily"));
      localStorage.removeItem(getCacheKey("puzzleNumber"));
    }

    function getCacheKey(cacheKey) {
      let suffix = lang === "en" ? "" : `-${lang}`;
      return cacheKey + suffix;
    }

    function getCache(cacheKey) {
      return localStorage.getItem(getCacheKey(cacheKey));
    }

    function setCache(cacheKey, cacheValue) {
      return localStorage.setItem(getCacheKey(cacheKey), cacheValue);
    }

    async function getDaily(){
      const cachedPuzzleNumber = getCache("puzzleNumber");
      const cachedPuzzleVersion = getCache("puzzleVersion");
      newPuzzle = (puzzleNumber != cachedPuzzleNumber);

      puzzleVersion = (await (await fetch("/game/version")).json()).version;

      const samePuzzle = (puzzleNumber == cachedPuzzleNumber);
      const sameVersion = (puzzleVersion === cachedPuzzleVersion);

      if ((!samePuzzle) || (!sameVersion)) {
        clearCache();
        setCache("puzzleNumber", puzzleNumber);
        setCache("puzzleVersion", puzzleVersion);
        const response = await fetch("/game/data");
        setCache("daily", JSON.stringify(await response.json()))
      }
      return JSON.parse(getCache("daily"));
    }

    function getCachedGuesses() {
		    guesses = JSON.parse(getCache("mmm_guesses") || "{}");
		    allGuesses = new Set(JSON.parse(getCache("mmm_allGuesses") || "[]"));
    }


  async function populate(newGuesses) {
    const noSpacePunctuation = "’'";
    const punctuation = ",." + noSpacePunctuation;
    const pic = document.getElementById("pic");
    const author = document.getElementById("promptBy")
    author.textContent = "prompt by " + daily.author;
    pic.src = daily.picture;
    const prompt = document.getElementById("prompt");
    prompt.replaceChildren([]);
    let won = true;
    for (let i = 0; i < daily.words.length; i++) {
      const word = guesses[i] || daily.words[i];
        var newWord;
        var wordWrapper = document.createElement("span");
        var wordCounter = document.createElement("p");
        wordCounter.classList = "word-counter"
        wordCounter.textContent = i + 1;
        if (word[0] === "█") {
          won = false;
          newWord = document.createElement("span");
          newWord.classList = "word caviarded word-length";
          newWord.setAttribute("data-word-length", word.length);
          newWord.textContent = word;
        }
        else {
          newWord = document.createElement("span");
          newWord.textContent = word;
          if (punctuation.includes(word)) {
            newWord.classList = "punct";
          }
          else if (newGuesses[i]) {
            newWord.classList = "word selected";
          }
        }
        wordWrapper.appendChild(newWord);
        wordWrapper.appendChild(wordCounter);
        prompt.appendChild(wordWrapper);
      }
      if (won) {
        markWin();
      }
  }

  function getWinMessage() {
    if (lang == "en") {
    return `<p><b>
            You won! 🎉 <br/>
            You found the daily MiMaMu in ${allGuesses.size} guesses! <br/>
            <a href="javascript:MiMaMu.share();" style="text-decoration: underline; color: cyan;">Share</a>
            and play again tomorrow!
            </b>
            <br/>
            </p>`
    } else if (lang == "he") {
    return `<p><b>
            ניצחת! 🎉 <br/>
            פתרת את ה־מי?מה?מו? היומי ב־${allGuesses.size} ניחושים! <br/>
            אפשר
            <a href="javascript:MiMaMu.share();" style="text-decoration: underline; color: cyan;">לשתף</a>
            ולשחק שוב מחר!
            </b>
            <br/>
            </p>`
    }
  }

  async function markWin() {
    document.getElementById("guess-text").disabled = true;
    document.getElementById("timer").hidden = false;
    const winMessage = document.getElementById("winMessage")
    winMessage.innerHTML = getWinMessage();
    twemoji.parse(winMessage);
  }

  async function submitGuess(event) {
    event.preventDefault();
    const guessField = document.getElementById("guess-text");
    const guess = guessField.value.trim();
    allGuesses.add(guess);
    const response = await fetch("/game/guess?guess_word=" + guess);
    const newGuesses = (await response.json()).correct_guesses;
    for (index in newGuesses) {
      guesses[index] = newGuesses[index];
    }
    setCache("mmm_guesses", JSON.stringify(guesses));
    setCache("mmm_allGuesses", JSON.stringify([...allGuesses]));
    await populate(newGuesses);
    guessField.value = "";
    guessField.focus();
  }

  const params = new URLSearchParams(window.location.search);
  const future = params.get('future');
  const token = params.get('mmm_token');
  let currentPage = 0;
  if (future) {
    currentPage = -1;
  }
  async function getHistory() {
    await fetchHistory();
    addClickListenersToImages();
    currentPage++;
  }
  async function fetchHistory() {
        let url = `/game/history?page=${currentPage}`;
        if (token) {
          url += `&mmm_token=${token}`;
        }
        const response = await fetch(url);
        riddle_history = await response.json();
        const imageContainer = document.getElementById('image-container');
        riddle_history.forEach((historia) => {
          const imgWrapper = document.createElement("div");
          imgWrapper.className = "column3";
          const imgText = document.createElement("p");
          imgText.textContent = historia.date;
          const imgElement = document.createElement('img');
          imgElement.className = 'column imageHistory';
          imgElement.style.borderRadius = "50%";
          imgElement.src = historia.picture;
          imgElement.setAttribute('data-prompt', historia.words.join(" "));
          imgWrapper.appendChild(imgElement);
          imgWrapper.appendChild(imgText);
          imageContainer.appendChild(imgWrapper);
        });
  }

    // Function to open the modal
    function openModal(imageUrl, prompt) {
        const modal = document.getElementById('image-modal');
        const modalImage = document.getElementById('modal-image');
        const modalWords = document.getElementById('modal-words');
        const modalContent = document.querySelector('.modal-content');

        modalImage.src = imageUrl;
        modalWords.textContent = prompt;

        modal.classList.add('open');
        modalContent.classList.add('open');

        modal.onclick = closeModal;

        // Close the modal when clicking outside of it
        window.onclick = function (event) {
            if (event.target === modal) {
            closeModal();
            }
        };
        }

        // Function to close the modal
    function closeModal() {
        const modal = document.getElementById('image-modal');
        const modalContent = document.querySelector('.modal-content');
        modal.classList.remove('open');
        modalContent.classList.remove('open');
    }

    // Function to add click event listeners to each image
    function addClickListenersToImages() {
    const images = document.querySelectorAll('.imageHistory');
        images.forEach((image) => {
            const imageUrl = image.src;
            const prompt = image.getAttribute('data-prompt');

        image.onclick = function () {
            openModal(imageUrl, prompt);
        };
    });
    }

  async function initGame() {
    const rawInitialDate = (await (await fetch("/game/first-date")).json()).first_date;
    initialDay = (new Date(rawInitialDate + "Z").getTime() / 86400000);
    puzzleNumber = today + 1 - initialDay;

    daily = await getDaily();
    getCachedGuesses();
    await populate({});
    const guessForm = document.getElementById("guess-form");
    const dalleLink = document.getElementById("dalle-link");
    guessForm.addEventListener("submit", submitGuess);
    document.getElementById("header").textContent = `${document.title} #${puzzleNumber}`;
    twemoji.parse(document.body);

    const dalleVersion = daily.dalle | 2;
    dalleLink.textContent = 'DALL·E ' + dalleVersion;
    if (dalleVersion == 2) {
      dalleLink.setAttribute("href", "https://openai.com/dall-e-2/")
    }
    else {
      dalleLink.setAttribute("href", "https://www.bing.com/images/create/")
    }

      var x = setInterval(function() {
        // Find the distance between now and the count down date
        var distance = tomorrow.getTime() - Date.now();
        if (distance < 0 && (!document.hidden)) {
            window.location.replace(location.protocol + '//' + location.host + location.pathname);
            return;
        }

        // Time calculations for days, hours, minutes and seconds
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Output the result in an element with id="demo"
        document.getElementById("timer").innerHTML = "next MiMaMu in " +
        hours + ":" + minutes.toString().padStart(2, '0') + ":" + seconds.toString().padStart(2, '0');

        // If the count down is over, write some text
    }, 1000);

  }

  function share() {
    // We use the stored guesses here, because those are not updated again
    // once you win -- we don't want to include post-win guesses here.
    const totalGuesses = JSON.parse(getCache("mmm_allGuesses")).length;
    const puzzleNumber = getCache("puzzleNumber");
    const hebrewText = `פתרתי את מי?מה?מו? #${puzzleNumber}
ב־${totalGuesses} ניחושים! 🖼️🤔

    #מימהמו
    https://mimamu.ishefi.com/lang/he
    `

    const englishText = `I solved MiMaMu #${puzzleNumber} in ${totalGuesses} guesses! 🖼️🤔

#MiMaMuGame
https://mimamu.ishefi.com/lang/en`
    var text;
    if (lang == "he") {
      text = hebrewText;
    } else {
      text = englishText;
    }
    const copied = ClipboardJS.copy(text);

    if (copied) {
        alert("Copied to clipboard");
    }
    else {
        alert("Failed to copy to clipboard");
    }
}


  return {
    share: share,
    initGame: initGame,
    getHistory: getHistory
  };
})();


function shareBtc() {
  const BTCAddress = "bc1qe3hpdddft34lmm7g6s6u6pef6k6mz4apykrla3jewapxeup4hpwsydhgx0";
  const copied = ClipboardJS.copy(BTCAddress);
  if (copied) {
      alert("copied BTC wallet address :)");
  }
  else {
      alert("Failed to copy to clipboard");
  }
}
