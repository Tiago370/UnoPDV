create table produto(
	id integer primary key autoincrement,
    	codigo text unique,
	descricao text,
	preco real
);

create table venda(
	id integer primary key autoincrement,
	data text
);

create table item_venda(
	id integer primary key autoincrement,
	venda_id integer,
	produto_id integer,
	quantidade real,
	preco_unit real,
	foreign key(venda_id) references venda(id),
	foreign key(produto_id) references produto(id)
);
