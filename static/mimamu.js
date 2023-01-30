let MiMaMu = (function () {
    const now = Date.now();
    const today = Math.floor(now / 86400000);
    const tomorrow = new Date();
    tomorrow.setUTCHours(24, 0, 0, 0);
    var daily, guesses;
    var allGuesses;

    const initialDay = 19382;
    const puzzleNumber = today + 1 - initialDay;

    function clearCache() {
      localStorage.removeItem("mmm_allGuesses");
      localStorage.removeItem("mmm_guesses");
      localStorage.removeItem("winState");
      localStorage.removeItem("daily");
      localStorage.removeItem("puzzleNumber");
    }

    async function getDaily(){
      const cachedPuzzleNumber = localStorage.getItem("puzzleNumber");
      const cachedPuzzleVersion = localStorage.getItem("puzzleVersion");
      newPuzzle = (puzzleNumber != cachedPuzzleNumber);

      puzzleVersion = (await (await fetch("/game/version")).json()).version;
      console.log(puzzleVersion);

      const samePuzzle = (puzzleNumber == cachedPuzzleNumber);
      const sameVersion = (puzzleVersion === cachedPuzzleVersion);

      if ((!samePuzzle) || (!sameVersion)) {
        clearCache();
        localStorage.setItem("puzzleNumber", puzzleNumber);
        localStorage.setItem("puzzleVersion", puzzleVersion);
        const response = await fetch("/game/data");
        localStorage.setItem("daily", JSON.stringify(await response.json()))
      }
      return JSON.parse(localStorage.getItem("daily"));
    }

    function getCachedGuesses() {
		    guesses = JSON.parse(localStorage.getItem("mmm_guesses") || "{}");
		    allGuesses = new Set(JSON.parse(localStorage.getItem("mmm_allGuesses") || "[]"));
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


  async function populate(newGuesses) {
    const punctuation = ","
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
        prompt.appendChild(newWord);
      }
      if (won) {
        markWin();
      }
  }

  function getWinMessage() {
    return `<p><b>
            You won! 🎉 <br/>
            You found the daily MiMaMu in ${allGuesses.size} guesses! <br/>
            <a href="javascript:share();" style="text-decoration: underline; color: cyan;">Share</a>
            and play again tomorrow!
            </b>
            <br/>
            </p>`
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
    localStorage.setItem("mmm_guesses", JSON.stringify(guesses));
    localStorage.setItem("mmm_allGuesses", JSON.stringify([...allGuesses]));
    await populate(newGuesses);
    guessField.value = "";
    guessField.focus();
  }

  async function init()  {
    twemoji.parse(document.body);
    daily = await getDaily();
    getCachedGuesses();
    await populate({});
    const guessForm = document.getElementById("guess-form");
    guessForm.addEventListener("submit", submitGuess);
    document.getElementById("header").textContent = "MiMaMu #" + puzzleNumber;
  }
  return {init: init};
})();

function share() {
    // We use the stored guesses here, because those are not updated again
    // once you win -- we don't want to include post-win guesses here.
    const totalGuesses = JSON.parse(localStorage.getItem("mmm_allGuesses")).length;
    const puzzleNumber = localStorage.getItem("puzzleNumber");
    const text = "I solved MiMaMu #" + puzzleNumber  + " in " + totalGuesses + " guesses! 🖼️🤔\n\n#MiMaMuGame\nhttps://mimamu.ishefi.com"
    const copied = ClipboardJS.copy(text);

    if (copied) {
        alert("Copied to clipboard");
    }
    else {
        alert("Failed to copy to clipboard");
    }
}


MiMaMu.init();
