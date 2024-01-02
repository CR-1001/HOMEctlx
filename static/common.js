/* This file is part of HomeCtl. Copyright (C) 2023 Christian Rauch.
   Distributed under terms of the GPL3 license. */

function set_input(selector, value) {
    $(selector)
        .attr("value", value)
        .css("visibility", value == "-" ? "collapse" : "visible")
}

function set_text(selector, text) {
    $(selector).text(text)
}

function set_color(selector, red1, gre1, blu1, red2, gre2, blu2) {

    col1 = to_rgb_css(red1, gre1, blu1, 1)
    col2 = to_rgb_css(red2, gre2, blu2, 1)
    
    $(selector).css(
        "background-image", 
        //"linear-gradient(to top, " + col0 + " 75%, " + col1 + " 25%)")
        "linear-gradient(to right, " + col1 + ", " + col2 + " )")
}

function set_visible(selector, is_visible) {
    element = $(selector)
    element.css("visibility", is_visible ? "visible" : "collapse")
}

function get_data(selector, key) {
    data_key = "data-" + key
    element = $(selector).closest("[" + data_key + "]")
    return element.attr(data_key)
}

function set_data(selector, key, value) {
    data_key = "data-" + key
    $(selector).attr(data_key, value)
}

function get_search_parameter(key, default_value=null) {
    value = new URLSearchParams(window.location.search).get(key)
    return value != null ? value : default_value
}

function set_search_parameter(key, value) {
    url = new URL(location);
    url.searchParams.set(key, value);
    history.replaceState({}, "", url)
}

function push_state_history_with_search_parameter(key, value) {
    url = new URL(location);
    url.searchParams.set(key, value);
    history.pushState({}, "", url)
}

function to_rgb_css(red, gre, blu, transparency) {
    return "rgb(" + red + ", " + gre + ", " + blu + ", " + transparency + ")"
}

function is_number(str) {
    number = /^[0-9]+$/.test(str)
    return number;
}