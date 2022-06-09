function on_load() {
	for (var i = 0; i < 10; i++) {
		edges.add(i);
		edges.add(99 - i);
		if (i < 8) {
			edges.add(10*(i+1));
			edges.add(10*(i+1) + 9);
		}
	}
	var grid = document.getElementById("grid");
	var border = document.getElementById("edges");
	for (var i = 0; i < 100; i++) {
		var sq = document.createElement("div");
		sq.id = i;
		if (!edges.has(i)) {
			sq.tag = ".";
			sq.className = "square";
		}
		else {
			sq.tag = "#";
			sq.className = "border";
		}
		if (i == 45 || i == 54) {
			var disk = document.createElement("div");
			disk.id = "d"+i;
			disk.className = "black-disk";
			sq.appendChild(disk);
			sq.tag = "x";
		}
		else if (i == 44 || i == 55) {
			var disk = document.createElement("div");
			disk.id = "d"+i;
			disk.className = "white-disk";
			sq.appendChild(disk);
			sq.tag = "o";
		}
		if (!edges.has(i))
			grid.appendChild(sq);
		else
			border.appendChild(sq);
	};
	var elem = document.getElementById("ai_turn");
	elem.innerHTML = "-";
	write_state();
	play();
};

function start_game() {
	var start_button = document.getElementById("start");
	start_button.disabled = true;
	var elem = document.getElementById("ai_turn");
	elem.innerHTML = ai_turn;
	var strat_button = document.getElementById("strategy_button");
	strat_button.click();
	var result = document.getElementById("result");
	result.innerHTML = "";
	var disk;
	var sq;
	if (!(last_move == -1)) {
		sq = document.getElementById(last_move);
		sq.className = "square";
		last_move = -1;
	}
	for (var i = 0; i < 100; i++) {
		sq = document.getElementById(i);
		if (i == 45 || i == 54) {
			disk = document.getElementById("d"+i);
			disk.className = "black-disk";
			sq.tag = "x";
		}
		else if (i == 44 || i == 55) {
			disk = document.getElementById("d"+i);
			disk.className = "white-disk";
			sq.tag = "o";
		}
		else {
			if (sq.childElementCount > 0)
				sq.removeChild(sq.firstElementChild);
			if (edges.has(i))
				sq.tag = "#";
			else
				sq.tag = ".";
		}
	}
	turn = "x";
	other = "o";
	black_score = 2;
	white_score = 2;
	ai_turn = ai_turn_buffer;
	write_state();
	update_score();
	update_icon();
	play();
	setTimeout(function() {
		start_button.disabled = false;
	}, 500); 
};

function play() {
	highlight_moves();
	if (turn === ai_turn)
		setTimeout(ai_move, 500);
};

function highlight_moves() {
	var moves = [];
	var dirs = [1, -9, -10, -11, -1, 9, 10, 11];
	var idx = null;
	var sq = null;
	var new_idx = null;
	var new_sq = null;
	for (var i = 1; i < 9; i++) {
		for (var j = 1; j < 9; j++) {
			idx = 10*i + j;
			sq = document.getElementById(idx);
			if (sq.tag === ".") {
				for (var k = 0; k < 8; k++) {
					new_idx = idx + dirs[k];
					new_sq = document.getElementById(new_idx);
					if (new_sq.tag === turn)
						continue;
					while (new_sq.tag === other) {
						new_idx += dirs[k];
						new_sq = document.getElementById(new_idx);
					}
					if (new_sq.tag === turn) {
						moves.push(idx);
						break;
					}
				}
			}
		}
	}
	for (var i = 0; i < 100; i++) {
		if (edges.has(i))
			continue;
		sq = document.getElementById(i);
		if (moves.includes(i)) {
			sq.className = "legal-move";
			if (!(turn === ai_turn)) {
				sq.onclick = function() {
					place_disk(this.id)
				};
			}
		}
		else if (!(i == last_move)) {
			sq.className = "square";
			sq.onclick = doNothing;
		}
	}
	return moves;
};

function place_disk(idx) {
	var sq = document.getElementById(idx);
	if (sq.childElementCount == 0) {
		sq.className = "last-move";
		last_move = idx;
		var disk = document.createElement("div");
		disk.id = "d"+idx;
		if (turn === "x") {
			disk.className = "black-disk";
			if (sq.tag === ".")
				black_score += 1;
			sq.tag = "x";
		}
		else {
			disk.className = "white-disk";
			if (sq.tag === ".")
				white_score += 1;
			sq.tag = "o";
		}
		
		sq.appendChild(disk);
		sq.onclick = doNothing;
		update_disks(parseInt(idx));
		update_score();
		
		pass_turn();
		moves = highlight_moves();
		var game_ended = false;
		if (moves.length == 0) {
			pass_turn();
			moves = highlight_moves();
			if (moves.length == 0) {
				end_game();
				game_ended = true;
			}
		}
		if (!game_ended) {
			update_score();
			update_icon();
		}
		write_state();
		if (!game_ended && turn === ai_turn) {
			setTimeout(ai_move, 100);
		}
	}
};

function update_disks(idx) {
	var dirs = [1, -9, -10, -11, -1, 9, 10, 11];
	var new_idx = null;
	var new_sq = null;
	for (var i = 0; i < 8; i++) {
		new_idx = idx + dirs[i];
		new_sq = document.getElementById(new_idx);
		if (new_sq.tag === turn)
			continue;
		while (new_sq.tag === other) {
			new_idx += dirs[i];
			new_sq = document.getElementById(new_idx);
		}
		if (new_sq.tag === turn) {
			while (!(new_idx == idx)) {
				new_idx -= dirs[i];
				if (new_idx == idx)
					break;
				disk = document.getElementById("d"+new_idx);
				new_sq = document.getElementById(new_idx);
				new_sq.className = "square";
				if (turn === "x") {
					disk.className = "black-disk";
					new_sq.tag = "x";
					black_score += 1;
					white_score -= 1;
				}
				else {
					disk.className = "white-disk";
					new_sq.tag = "o";
					white_score += 1;
					black_score -= 1;
				}
			}
		} 
	}
};

function pass_turn() {
	var temp = turn;
	turn = other;
	other = temp;
};

function update_score() {
	var score1 = document.getElementById("score1");
	var score2 = document.getElementById("score2");
	if (ai_turn === "x") {
		score1.innerHTML = "AI Bot: " + black_score;
		score2.innerHTML = "Player: " + white_score;
	}
	else if (ai_turn === "o") {
		score1.innerHTML = "Player: " + black_score;
		score2.innerHTML = "AI Bot: " + white_score;
	}
	else {
		score1.innerHTML = "Player: " + black_score;
		score2.innerHTML = "Player: " + white_score;
	}
};

function update_icon() {
	var black_icon = document.getElementById("black-icon");
	var white_icon = document.getElementById("white-icon");
	if (turn === "x") {
		black_icon.className = "black-disk-icon";
		white_icon.className = "blank-icon";
	}
	else {
		white_icon.className = "white-disk-icon";
		black_icon.className = "blank-icon";
	}
};

function write_state() {
	var sq;
	var new_state = turn;
	for (var i = 0; i < 100; i++) {
		sq = document.getElementById(i);
		new_state += sq.tag;
	}
	var state = document.getElementById("state");
	state.innerHTML = new_state;
}

function end_game() {
	var elem = document.getElementById("result");
	var str = "";
	if (black_score > white_score)
		str = "Black wins!";
	else if (white_score > black_score)
		str = "White wins!";
	else
		str = "Tie!"
	elem.innerHTML = str;
	var black_icon = document.getElementById("black-icon");
	var white_icon = document.getElementById("white-icon");
	black_icon.className = "black-disk-icon";
	white_icon.className = "white-disk-icon";
};

function ai_move() {
	var button = document.getElementById("move_button");
	button.click();
	var move = document.getElementById("move").innerHTML;
	if (!(move === "")) {
		move = parseInt(move);
		place_disk(move);
	}
};

function ai_on(button) {
	button.style.textDecoration = "underline";
	button.onmouseout = function() { button.style.textDecoration = "underline"; };
}

function ai_off(button) {
	button.style.textDecoration = "none";
	button.onmouseover = function() { button.style.textDecoration = "underline"; };
	button.onmouseout = function() { button.style.textDecoration = "none"; };
};

function set_ai_black() {
	ai_turn_buffer = "x";
	var ai_black = document.getElementById("ai_black");
	var ai_none = document.getElementById("ai_none");
	var ai_white = document.getElementById("ai_white");
	ai_on(ai_black);
	ai_off(ai_none);
	ai_off(ai_white);
};

function set_ai_none() {
	ai_turn_buffer = "-";
	var ai_black = document.getElementById("ai_black");
	var ai_none = document.getElementById("ai_none");
	var ai_white = document.getElementById("ai_white");
	ai_off(ai_black);
	ai_on(ai_none);
	ai_off(ai_white);
};

function set_ai_white() {
	ai_turn_buffer = "o";
	var ai_black = document.getElementById("ai_black");
	var ai_none = document.getElementById("ai_none");
	var ai_white = document.getElementById("ai_white");
	ai_off(ai_black);
	ai_off(ai_none);
	ai_on(ai_white);
};

function doNothing() {

};