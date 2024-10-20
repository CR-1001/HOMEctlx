/* This file is part of HOMEctlx. Copyright (C) 2024 Christian Rauch.
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

    if (tiles.length == 0) {
        for (let i = 0; i < tilesToCreate; i++) {
            createTile();
        }
    }
    else {
        tilesToChange = Math.floor(Math.random() * tilesToCreate * 0.4);
    }

    changeTilesColor();
    changeBaseColor();
    
    setTimeout(changeTiles, 3000 + Math.random() * 6000);
}

function changeBaseColor() {
    const minute = new Date().getMinutes();
    if      (minute === 0  || minute === 30) colorBase = "#FF0000";
    else if (minute === 5  || minute === 35) colorBase = "#00FFFF";
    else if (minute === 10 || minute === 40) colorBase = "#FFFF00";
    else if (minute === 15 || minute === 45) colorBase = "#FF00FF";
    else if (minute === 20 || minute === 50) colorBase = "#00FF00";
    else if (minute === 25 || minute === 55) colorBase = "#0000FF";
    else {
        if (Math.random() < 0.4) {
            colorBase = combineColors(colorBase, getRandomColor());
        }
    }

    if (Math.random() < 0.2) {
        colorBasePart = Math.floor(Math.random() * 3);
    }
}

function createTile() {

    tileSizePercentage = (Math.random() < 0.5) 
        ? Math.random() * 30 + 8
        : Math.max(8, tileSizePercentage * Math.random());

    const tile = document.createElement('div');
    tile.classList.add('tile');
    tile.classList.add(`tile-${Math.random() < 0.05 ? "round" : "straight"}`);

    size = Math.min(window.innerHeight, window.innerHeight) / 100 * tileSizePercentage;

    tile.style.position = 'absolute';
    tile.style.width = `${size}px`;
    tile.style.height = `${size}px`;

    if (Math.random() < 0.3 || randomX == 0 || randomY == 0) {
        randomX = Math.random() * (window.innerWidth - size);
        randomY = Math.random() * (window.innerHeight - size);
    }
    else {
        if (Math.random() < 0.4) randomX = randomX * Math.random();
        if (Math.random() < 0.4) randomY = randomY * Math.random();
    }

    if (Math.random() < 0.5) tile.style.left = `${randomX}px`;
    else tile.style.right = `${randomX}px`;

    if (Math.random() < 0.5) tile.style.top = `${randomY}px`;
    else tile.style.bottom = `${randomY}px`;

    const grid = document.querySelector('.background-grid');
    grid.appendChild(tile);
}

function createEmoji() {
    const grid = document.querySelector('.background-grid');
    
    const categories = {
        //cat1: ["Hello", "Hola", "Bonjour", "Hallo", "Ciao", "Olá", "Здравствуйте", "你好", "こんにちは", "안녕하세요", "مرحبا", "नमस्ते", "Habari", "Hallo", "Γειά σας", "שלום", "Merhaba", "สวัสดี", "Xin chào", "হ্যালো"],
        cat2: ["☀️", "🌍", "🪐", "🛰️", "🌕"],
        cat3: ["☕", "👾", "⭐", "💣", "👻", "😵‍💫", "🌘", "🍌", "🔥"],
        cat4: ["🍌", "🍉", "🍇", "🍓", "🍔", "🍕", "🍦", "🍬", "🍭"],
        cat5: ["🌳", "🌴", "🐒", "🦧", "🐘", "🐁", "🦉", "🦋", "🐦", "🕷️", "🦩"],
        cat6: ["🦀", "🦑", "🐙", "🦈", "🐬", "🐟", "🐋", "🦐", "🦞", "🐠"],
    };

    const categoryNames = Object.keys(categories);
    const chosenCategoryName = categoryNames[Math.floor(Math.random() * categoryNames.length)];
    const chosenCategory = categories[chosenCategoryName];
    
    const shuffledCategory = chosenCategory.sort(() => 0.5 - Math.random());
    
    const numEmojis = Math.floor(Math.random() * 3) + 1;
    
    const uniqueSymbols = shuffledCategory.slice(0, numEmojis);
    
    for (const symbol of uniqueSymbols) {
        const tile = document.createElement('div');
        tile.classList.add('emoji');
        
        tile.innerHTML = symbol;
        
        tile.style.position = 'absolute';
        tile.style.left = `${Math.random() * 25}em`;
        tile.style.top = `${5 + Math.random() * 25}em`;

        grid.appendChild(tile);
    }
}

function changeTilesColor() {
    const tiles = document.querySelectorAll('.tile');
    const total = tiles.length;

    for (let i = 0; i < tilesToChange; i++) {
        const randomIndex = Math.floor(Math.random() * total);
        const tile = tiles[randomIndex];
        
        const color = getRandomColor();
        tile.style.backgroundColor = combineColors(colorBase, color);
    }
}

function combineColors(color1, color2) {
    let newColor;
    if (colorBasePart === 0) {
        newColor = `#${color2.slice(1, 3)}${color1.slice(3, 5)}${color1.slice(5, 7)}`;
    } else if (colorBasePart === 1) {
        newColor = `#${color1.slice(1, 3)}${color2.slice(3, 5)}${color1.slice(5, 7)}`;
    } else {
        newColor = `#${color1.slice(1, 3)}${color1.slice(3, 5)}${color2.slice(5, 7)}`;
    }

    return newColor;
}

let colorBase = "#00FFFF";
let colorBasePart = 0;
let randomX = 0;
let randomY = 0;
let tilesToCreate = 30;
let tilesToChange = 10;
let tileSizePercentage = 10;
let style = Math.random() < 0.2 ? "round" : "straight";

document.addEventListener('DOMContentLoaded', function() {
    changeTiles();
    createEmoji();
});
