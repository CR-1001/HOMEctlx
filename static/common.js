/* This file is part of HomeCtl. Copyright (C) 2024 Christian Rauch.
   Distributed under terms of the GPL3 license. */

/*
Common.
*/

function setInput(selector, value) {
    const element = document.querySelector(selector);
    if (element) {
        element.setAttribute("value", value);
        element.style.visibility = value === "-" ? "collapse" : "visible";
    }
}

function setText(selector, text) {
    const element = document.querySelector(selector);
    if (element) {
        element.textContent = text;
    }
}

function setColor(selector, red1, gre1, blu1, red2, gre2, blu2) {
    const element = document.querySelector(selector);
    if (element) {
        const col1 = toRgbCss(red1, gre1, blu1, 1);
        const col2 = toRgbCss(red2, gre2, blu2, 1);
        element.style.backgroundImage = `linear-gradient(to right, ${col1}, ${col2})`;
    }
}

function setVisible(selector, isVisible) {
    const element = document.querySelector(selector);
    if (element) {
        element.style.visibility = isVisible ? "visible" : "collapse";
    }
}

function getData(selector, key) {
    const dataKey = `data-${key}`;
    const element = document.querySelector(selector);
    if (element) {
        const closestElement = element.closest(`[${dataKey}]`);
        return closestElement ? closestElement.getAttribute(dataKey) : null;
    }
    return null;
}

function setData(selector, key, value) {
    const element = document.querySelector(selector);
    if (element) {
        const dataKey = `data-${key}`;
        element.setAttribute(dataKey, value);
    }
}

function getSearchParameter(key, defaultValue = null) {
    const value = new URLSearchParams(window.location.search).get(key);
    return value !== null ? value : defaultValue;
}

function setSearchParameter(key, value) {
    const url = new URL(location);
    url.searchParams.set(key, value);
    history.replaceState({}, "", url);
}

function pushStateHistoryWithSearchParameter(key, value) {
    const url = new URL(location);
    url.searchParams.set(key, value);
    history.pushState({}, "", url);
}

function toRgbCss(red, gre, blu, transparency) {
    return `rgb(${red}, ${gre}, ${blu}, ${transparency})`;
}

function isNumber(str) {
    return /^[0-9]+$/.test(str);
}

function clean(text) {
    return text.replace(/\n/g, '<br>').replace(/\s/g, '&nbsp;');
}

function invertSelection(container) {
    const checkboxes = document.querySelectorAll(`${container} :checkbox`);
    checkboxes.forEach(checkbox => {
        checkbox.checked = !checkbox.checked;
    });
}

function bringIntoView(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'instant', block: 'start' });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('logo').addEventListener('click', function() {
        var menus = document.getElementsByClassName('menu');
        Array.prototype.forEach.call(menus, function(menu) {
            menu.classList.toggle('hidden');
        });
    });
});
