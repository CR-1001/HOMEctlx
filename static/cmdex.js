/* This file is part of HOMEctlx. Copyright (C) 2024 Christian Rauch.
   Distributed under terms of the GPL3 license. */

/*
Handles view-model functionalities, collects arguments entered in fields, and  
calls server functions.
*/

document.addEventListener('DOMContentLoaded', function() {
    initialize();

    // react to command
    let debounceTimer;
    document.addEventListener("click", function(event) {
        if (event.target.matches(".execute, input.execute")) {
            process(event.target);
        }
    });

    document.addEventListener("input", function(event) {
        if (event.target.matches(".execute, input.execute")) {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(function() {
                process(event.target);
            }, 400);
        }
    });

    // invert selection in multiple-selection fields
    document.addEventListener("click", function(event) {
        if (event.target.matches(".invert-selection")) {
            invertSelection(event.target.parentElement);
        }
    });

    // bring into view
    document.addEventListener("click", function(event) {
        if (event.target.matches(".bring_into_view")) {
            const containerId = event.target.dataset.container;
            setTimeout(function() {
                bringIntoView(containerId);
            }, 1000);
        }
    });
});

function process(sourceElement) {
    if (document.querySelectorAll(".execute.inactive").length > 0) return;
    
    const func = sourceElement.dataset.func;
    const form = sourceElement.closest("form");
    const fieldset1 = sourceElement.closest("fieldset");
    const fieldset2 = sourceElement.closest(".fieldset");

    let wait = false;
    const args = {};
    
    [form, fieldset1, fieldset2].forEach(function(container) {
        if (!container) return;
        container.querySelectorAll("input, select, textarea").forEach(function(elem) {
            const key = elem.name;
            if (key === undefined || key === "") return;

            // Handle select, textarea elements
            if (elem.matches("input[type='text'], textarea, select")) {
                args[key] = elem.value;
            } else if (elem.matches("input")) {
                const value = elem.value;
                
                // Case multiple selected options
                if (elem.type === "checkbox") {
                    if (!args.hasOwnProperty(key)) {
                        args[key] = [];
                    }
                    if (elem.checked) {
                        args[key].push(value);
                    }
                } else if (elem.type === "file") {
                    const files = elem.files;
                    const filesCount = files.length;
                    if (filesCount === 0) return;
                    wait = true;
                    let fileUpload = 0;

                    for (let i = 0; i < files.length; i++) {
                        const file = files[i];
                        const fileReader = new FileReader();
                        const filename = file.name;

                        fileReader.onload = function(event) {
                            if (!args[key]) {
                                args[key] = {
                                    "names": [],
                                    "bytes": []
                                };
                            }
                            
                            args[key]["names"].push(filename);
                            args[key]["bytes"].push(event.target.result);
                            
                            fileUpload++;
                            if (fileUpload === filesCount) {
                                wait = false;
                            }
                        };
                        fileReader.readAsDataURL(file);
                    }
                } else {
                    args[key] = value;
                }
            }
        });
    });

    // triggers
    const param = sourceElement.dataset.param;
    if (param) {
        args[param] = sourceElement.dataset.value;
    }

    function waitAndExecute() {
        if (!wait) {
            execute(func, args);
        } else {
            // TODO: progress visualization
            setTimeout(waitAndExecute, 1000);
        }
    }

    waitAndExecute(func, args);
}

// initialize module (extract view-model, function, and arguments from the URL)
function initialize() {
    enable(false);

    const parts = window.location.pathname.split('/');
    const func = `${parts[1]}/${parts[2]}`;

    const params = {};
    const searchParams = new URLSearchParams(window.location.search);
    searchParams.forEach(function(value, key) {
        params[key] = value;
    });

    execute(func, params);
}

// execute a command and refresh view
function execute(func, args) {
    // execute the command
    fetch(`/${func}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(args)
    })
    .then(response => response.json())
    .then(views => {
        Object.keys(views).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                element.outerHTML = views[key];
                handleAutoUpdate(key);
            }
        });
        enable(true);
    })
    .catch(error => {
        console.error("Error during execution:", error);
        enable(true);
    });
}

// handle auto-update
const processedAutoUpdates = new Set();
function handleAutoUpdate(key) {
    if (processedAutoUpdates.has(key)) return;
    processedAutoUpdates.add(key);
    
    const updatedElement = document.getElementById(key);
    updatedElement.querySelectorAll('[data-autoupdatedelay]')
        .forEach(elem => {
            const delay = elem.dataset.autoupdatedelay;
            setTimeout(function() { 
                processedAutoUpdates.delete(key); 
                process(elem);
            }, delay);
        });
}

// enable or disable controls   
function enable(active) {
    controls = document.querySelectorAll(".execute");
    if (active) {
        controls.forEach(el => el.classList.remove("inactive"));
    }
    else {
        controls.forEach(el => el.classList.add("inactive"));
    }
}