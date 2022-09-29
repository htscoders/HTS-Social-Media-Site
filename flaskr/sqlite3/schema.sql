DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS comment;
DROP TABLE IF EXISTS directmessage;

CREATE TABLE user (
    id          INTEGER CHECK(id > 0),
    username    TEXT    UNIQUE NOT NULL,
    password    TEXT    NOT NULL CHECK(length(password) >= 8),
    views       INTEGER DEFAULT 0 NOT NULL,
    timestamp  DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE post (
    id          INTEGER CHECK(id > 0),
    authorid    INTEGER NOT NULL,
    title       TEXT    NOT NULL,
    content     TEXT    NOT NULL,
    views       INTEGER DEFAULT 0 NOT NULL,
    timestamp  DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(authorid) REFERENCES user(id)
);

CREATE TABLE comment (
    id          INTEGER CHECK(id > 0),
    postid      INTEGER NOT NULL,
    authorid    INTEGER NOT NULL,
    replyingid  INTEGER NULL CHECK(replyingid != id),
    content     TEXT    NOT NULL,
    timestamp  DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(postid) REFERENCES user(id),
    FOREIGN KEY(authorid) REFERENCES user(id),
    FOREIGN KEY(replyingid) REFERENCES comment(id)
);

CREATE TABLE directmessage (
    id          INTEGER CHECK(id > 0),
    content     TEXT    NOT NULL,
    authorid    INTEGER NOT NULL CHECK(authorid != recipientid),
    recipientid INTEGER NOT NULL CHECK(recipientid != authorid),
    replyingid  INTEGER NULL CHECK(replyingid != id),
    timestamp  DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(authorid) REFERENCES user(id),
    FOREIGN KEY(recipientid) REFERENCES user(id),
    FOREIGN KEY(replyingid) REFERENCES directmessage(id)
);