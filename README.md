# letzguess_bot

A bot for playing LetzGuess
- - -

## Python version:
This version does not work anymore, it will probably get you banned.

## Tampermonkey version:
* Tested in Firefox with Tampermonkey v5.1.0
### Installation:
1. Install the `Tampermonkey` plug-in
2. Go to [https://www.letzguess.lu/](https://www.letzguess.lu/)
3. Create a new Tampermonkey script from the top bar (Tampermonkey>Create new script)
4. Copy the content of [main.js](https://github.com/UnKabaraQuiDev/letzguess_bot/blob/main/tampermonkey_js/main.js) into the new script
5. Save an go back to LetzGuess [LetzGame > Game > Challenge](https://www.letzguess.lu/game/challenge)
6. Refresh the page to enable the script
* Press `F` to auto-fill the correct answer (if saved)
* Press `Space` to continue to the next question.
<br>
*Note: This scripts will make a lot of mistakes at the beginning but will gradually become better as it saves the correct answers.*
### Settings:
There are a few settings in the tampermonkey script file:
* `random_failure`: The percentage rate to make a mistake even if the answer is known.
* `max_streak`: Limit the maximum correct answer streak.
* `no_error`: Override `random_failure`.

