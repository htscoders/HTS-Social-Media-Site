"use strict";
let apiURL = "/";
let userViewURL = "/";
window.addEventListener("load", function () {
    var _a, _b;
    apiURL = (_a = document.getElementById("api-endpoint-carrier").dataset) === null || _a === void 0 ? void 0 : _a["postfetchreplies"];
    userViewURL = (_b = document.getElementById("api-endpoint-carrier").dataset) === null || _b === void 0 ? void 0 : _b["userview"];
    window.addEventListener("click", function (e) {
        if (e.target instanceof HTMLElement) {
            if (e.target.parentElement) {
                const id = (e.target.id || e.target.parentElement.id).split("-");
                if (id[0] == "comment") {
                    getReplies(id[1]).then(function (comments) {
                        try {
                            const commentReplyContainer = document.getElementById(`comment-${id[1]}-replies`);
                            commentReplyContainer.innerHTML = "";
                            for (let i = 0; i < comments.length; i++) {
                                const comment = comments[i];
                                commentReplyContainer.innerHTML += `<li><b>${comment.content}</b> <a href="${userViewURL.replace("0", comment.authorid)}">${comment.author}</a> on ${comment.timestamp}</li>`;
                            }
                        }
                        catch (e) {
                            console.error(e);
                        }
                    }).catch(function () { throw new Error(`Tried fetching replies from nonexistent comment. (id${id})`); });
                }
            }
        }
    });
});
function getReplies(commentid) {
    return new Promise(function (resolve, reject) {
        const request = new XMLHttpRequest();
        request.addEventListener("readystatechange", function () {
            if (request.readyState == 4)
                if (request.status == 200)
                    resolve(JSON.parse(request.responseText).body);
                else if (request.status == 400)
                    reject();
                else
                    throw new Error(`Received status ${request.status} while retrieving CommentID${commentid}`);
        });
        request.open("POST", apiURL.replace("0", commentid));
        request.send();
    });
}
//# sourceMappingURL=getreplies.js.map