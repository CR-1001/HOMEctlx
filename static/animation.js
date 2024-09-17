/* This file is part of HomeCtl. Copyright (C) 2024 Christian Rauch.
   Distributed under terms of the GPL3 license. */

/*
Animations.
*/

function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function changeTiles() {
    const grid = document.querySelector('.background-grid');
    const tiles = grid.querySelectorAll('.tile');

    if (tiles.length > 0) {
        if (Math.random() < 0.2) {
            const randomIndex = Math.floor(Math.random() * tiles.length);
            const tileToRemove = tiles[randomIndex];
            grid.removeChild(tileToRemove);
        }
        if (Math.random() < 0.2) {
            createTile();
        }
    } else {
        const count = 20;
        for (let i = 0; i < count; i++) {
            createTile();
        }
    }

    changeTilesColor();
    changeBaseColor();
    
    setTimeout(changeTiles, 500 + Math.random() * 6000);
}

function changeBaseColor() {
    const minute = new Date().getMinutes();
    if      (minute === 0  || minute === 30) color_base = "#FF0000";
    else if (minute === 5  || minute === 35) color_base = "#00FFFF";
    else if (minute === 10 || minute === 40) color_base = "#FFFF00";
    else if (minute === 15 || minute === 45) color_base = "#FF00FF";
    else if (minute === 20 || minute === 50) color_base = "#00FF00";
    else if (minute === 25 || minute === 55) color_base = "#0000FF";
    else {
        if (Math.random() < 0.2) {
            color_base = combineColors(color_base, getRandomColor());
        }
    }

    if (Math.random() < 0.2) {
        color_base_part = Math.floor(Math.random() * 3);
    }
}

function createTile() {
    const tileSizePercentage = Math.random() * 25 + 5;

    const tile = document.createElement('div');
    tile.classList.add('tile');

    const size = Math.min(window.innerHeight, window.innerHeight) / 100 * tileSizePercentage;

    tile.style.position = 'absolute';
    tile.style.width = `${size}px`;
    tile.style.height = `${size}px`;

    const randomX = Math.random() * ((window.innerWidth * 0.8) - size);
    const randomY = Math.random() * ((window.innerHeight * 0.8) - size);

    tile.style.left = `${randomX}px`;
    tile.style.top = `${randomY}px`;

    const grid = document.querySelector('.background-grid');
    grid.appendChild(tile);
}

function changeTilesColor() {
    const tiles = document.querySelectorAll('.tile');
    const total = tiles.length;
    const tilesToChange = Math.floor(Math.random() * total * 0.2);

    for (let i = 0; i < tilesToChange; i++) {
        const randomIndex = Math.floor(Math.random() * total);
        const tile = tiles[randomIndex];
        
        const color = getRandomColor();
        tile.style.backgroundColor = combineColors(color_base, color);
    }
}

function combineColors(color1, color2) {
    let newColor;
    if (color_base_part === 0) {
        newColor = `#${color2.slice(1, 3)}${color1.slice(3, 5)}${color1.slice(5, 7)}`;
    } else if (color_base_part === 1) {
        newColor = `#${color1.slice(1, 3)}${color2.slice(3, 5)}${color1.slice(5, 7)}`;
    } else {
        newColor = `#${color1.slice(1, 3)}${color1.slice(3, 5)}${color2.slice(5, 7)}`;
    }

    return newColor;
}

let color_base = "#00FFFF";
let color_base_part = 0;

document.addEventListener('DOMContentLoaded', function() {
    changeTiles();
});
