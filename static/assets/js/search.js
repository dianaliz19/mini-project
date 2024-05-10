document.addEventListener("DOMContentLoaded", function() {
    var keyword = ["helo", "hi", "example", "search", "event", "functionality"]; // Update with your desired keywords
    autocomplete(document.getElementById("myInput"), keyword);
});

function autocomplete(inp, arr) {
    console.log("Autocomplete function called");
    inp.addEventListener("input", function(e) {
        var val = this.value.toLowerCase();
        var suggestions = arr.filter(word => word.toLowerCase().startsWith(val));
        displaySuggestions(suggestions);
    });

    document.addEventListener("click", function(e) {
        if (!e.target.classList.contains('suggestion') && !e.target.matches('#myInput')) {
            clearSuggestions();
        }
    });

    inp.addEventListener("keydown", function(e) {
        if (e.keyCode === 13) { // Check if Enter key is pressed
            var keyword = this.value.trim();
            if (keyword !== "") {
                performSearch(keyword);
                clearHighlights();
                highlightKeyword(keyword);
            }
        }
    });

    function performSearch(keyword) {
        // Implement your search logic here
        // For example, you can redirect to a search results page or filter content based on the keyword
        // In this example, let's just log the keyword to the console
        console.log("Performing search for keyword:", keyword);
    }

    function highlightKeyword(keyword) {
        var body = document.body;
        var regex = new RegExp(keyword, 'gi'); // Create a regular expression to match the keyword globally and case-insensitively
        var textNodes = getTextNodes(body);
        textNodes.forEach(function(node) {
            var newText = node.nodeValue.replace(regex, '<span style="background-color: yellow;">$&</span>');
            var temp = document.createElement('div');
            temp.innerHTML = newText;
            while (temp.firstChild) {
                node.parentNode.insertBefore(temp.firstChild, node);
            }
            node.parentNode.removeChild(node);
        });
    }

    function displaySuggestions(suggestions) {
        var suggestionBox = document.getElementById("suggestion-box");
        suggestionBox.innerHTML = '';
        suggestions.forEach(function(word) {
            var suggestion = document.createElement("div");
            suggestion.className = "suggestion";
            suggestion.textContent = word;
            suggestion.addEventListener("click", function() {
                inp.value = word;
                clearSuggestions();
                performSearch(word);
                clearHighlights();
                highlightKeyword(word);
            });
            suggestionBox.appendChild(suggestion);
        });
    }

    function clearSuggestions() {
        document.getElementById("suggestion-box").innerHTML = '';
    }

    function getTextNodes(node) {
        var textNodes = [];
        if (node.nodeType == Node.TEXT_NODE) {
            textNodes.push(node);
        } else {
            var children = node.childNodes;
            for (var i = 0; i < children.length; i++) {
                textNodes.push.apply(textNodes, getTextNodes(children[i]));
            }
        }
        return textNodes;
    }

    function clearHighlights() {
        var highlights = document.querySelectorAll('span[style="background-color: yellow;"]');
        highlights.forEach(function(element) {
            var text = element.textContent;
            element.parentNode.replaceChild(document.createTextNode(text), element);
        });
    }
}
