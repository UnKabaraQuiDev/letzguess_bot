// ==UserScript==
// @name     Letzguess help
// @version  1
// @grant    GM.getValue
// @grant    GM.setValue
// @match  https://www.letzguess.lu/game/challenge*
// @run-at   document-start
// ==/UserScript==

(function() {
    'use strict';

    const random_failure = 14; // /100%
    const max_streak = 160;
    const no_error = false;

    var round_env = undefined;
    var question_id = undefined;
    var saved_answer = undefined;

    function get_available_answers() {
        if(round_env === undefined) {
            round_env = document.querySelector('.game-challenge-round');
            if (!round_env) {
                console.log("No element with class .game-challenge-round found");
                return;
            }
        }

        const roundAnswers = round_env.querySelector('.game-challenge-round-responses');
        if (roundAnswers) {
            const innerHTMLValues = {};

            roundAnswers.querySelectorAll("button").forEach(child => {
                if (child.nodeType === Node.ELEMENT_NODE) {
                    innerHTMLValues[child.textContent] = child;
                }
            });
            //console.log(innerHTMLValues);
            return innerHTMLValues;
        } else {
            console.log("No element with class .game-challenge-round-responses found inside .game-challenge-round");
        }
        return undefined;
    }

    function click(buttonToClick) {
        console.log("click", buttonToClick);
        if(!buttonToClick) {
            console.log("Button is null");
            return;
        }
        buttonToClick.click();
        return;
    }

    function get_random_element_exclude(array, exclude) {
        var keys = Object.keys(array);
        delete keys[exclude];
        return array[keys[Math.floor(Math.random() * keys.length)]];
    }

    function get_random_element(array) {
        var keys = Object.keys(array);
        return array[keys[Math.floor(Math.random() * keys.length)]];
    }

    function get_random_element_array(array) {
        return array[Math.floor(Math.random() * array.length)];
    }

    function get_current_streak() {
        const parentElement = Array
        .from(document.querySelectorAll('p'))
        .find(el => el.innerHTML === 'Streak').parentNode;
        return parseInt(parentElement.querySelector('h2').innerHTML);
    }

    function next() {
        const nextBtn = document.querySelector("div.game-challenge-round-next > button");
        click(nextBtn);
    }


    // Function to run when the shortcut is pressed
    async function runScript() {
        var buttons = get_available_answers();
        console.log("buttons:", buttons);

        if(saved_answer == undefined) {
            // well well
            console.log("Well well");
        }else {
            click(buttons[saved_answer]);
        }

    }

    async function saveResponse(question_id, correct_answer) {
        console.log("setting: ", question_id, correct_answer);
        if(correct_answer === undefined || saved_answer === "undefined")
            return;
        await GM.setValue(question_id, correct_answer);
    }

    async function loadResponse(question_id, available_answers, current_streak) {
        saved_answer = await GM.getValue(question_id);

        if(saved_answer === undefined || saved_answer === "undefined") {
            console.log("No saved answer found for: ", question_id);

            saved_answer = get_random_element_array(available_answers);

            console.log("Random: ", saved_answer);
        }else {
            console.log("Saved answer found for: ", question_id, saved_answer);
        }

        if (Math.random()*100 < random_failure && !no_error) {
            saved_answer = get_random_element_array(available_answers);
            console.log("Changed answer, random = ", saved_answer);
        }

        const streak = current_streak;
        console.log("Current streak: ", streak);
        if (max_streak == streak) {
            saved_answer = get_random_element_exclude(available_answers, saved_answer);
            console.log("Changed answer, max_streak = ", saved_answer);
        }
    }

    var originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url) {
        console.log('Outgoing HTTP request intercepted:', method, url);
        // You can modify the request here if needed

        // Store reference to the XMLHttpRequest object
        var self = this;

        // Attach an event listener for the load event
        this.addEventListener('load', function() {
            // Check if the response is JSON
            var contentType = self.getResponseHeader('Content-Type');
            //console.log("content ", url, self.responseText);
            //console.log("Loaded: ", url);
            if (contentType && contentType.indexOf('application/json') !== -1) {
                if(!url.match(".+\/round\/([0-9]+)")) {
                    return;
                }

                // Parse the JSON response
                var jsonResponse = JSON.parse(self.responseText);
                console.log('JSON Response:', url, jsonResponse);
                // You can further process the JSON response here

                if(jsonResponse.round.ended || jsonResponse.round.question.correct_response) {
                    saveResponse(jsonResponse.round.question.question_id, jsonResponse.round.question.correct_response);
                }else if(!jsonResponse.round.ended) {
                    loadResponse(jsonResponse.round.question.question_id, jsonResponse.round.question.responses, jsonResponse.round.streak);
                }
            }
        });

        // Call the original open method
        originalOpen.apply(this, arguments);
    };


    // Define the keyboard shortcut (e.g., Ctrl + Shift + F)
    const shortcutKey = 'f';
    // const modifierKeys = ['ctrlKey', 'shiftKey'];

    GM.listValues().then(t => t.forEach(async v => console.log(v+": ", await GM.getValue(v))), b => console.log("Could not list values", b));

    // Event listener for keydown event
    document.addEventListener('keydown', function(event) {
        // console.log(event);
        if (event.key == shortcutKey/* && modifierKeys.every(key => event[key])*/) {
            event.stopPropagation();
            runScript();
        }else if(event.key == ' ') {
            event.stopPropagation();
            next();
        }
    });
})();
