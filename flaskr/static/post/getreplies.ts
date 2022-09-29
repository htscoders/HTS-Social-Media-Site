interface APIComment {
    id: number,
    authorid: string,
    author: string,
    content: string,
    timestamp: string,
    postid?: number,
    replyingid?: number,
}

let apiURL: string = "/";
let userViewURL: string = "/";

window.addEventListener("load", function() {
    apiURL = (document.getElementById("api-endpoint-carrier") as HTMLDivElement).dataset?.["postfetchreplies"] as string;
    userViewURL = (document.getElementById("api-endpoint-carrier") as HTMLDivElement).dataset?.["userview"] as string;

    window.addEventListener("click", function(e) {
        if (e.target instanceof HTMLElement) {
            if (e.target.parentElement) {
                const id: string[] = (e.target.id || e.target.parentElement.id).split("-");
                if (id[0] == "comment") {
                    getReplies(id[1]).then(function(comments) {
                        try {
                            const commentReplyContainer = document.getElementById(`comment-${id[1]}-replies`) as HTMLUListElement;
                            commentReplyContainer.innerHTML = "";
                            for (let i = 0;i < comments.length;i++) {
                                const comment = comments[i];
                                commentReplyContainer.innerHTML += `<li><b>${comment.content}</b> <a href="${userViewURL.replace("0", comment.authorid)}">${comment.author}</a> on ${comment.timestamp}</li>`;
                            }
                        } catch (e) {
                            console.error(e);
                        }
                    }).catch(function() {throw new Error(`Tried fetching replies from nonexistent comment. (id${id})`)});
                }
            }
        }
    });
});

function getReplies(commentid: string): Promise<APIComment[]> {
    return new Promise(function(resolve, reject) {
        const request = new XMLHttpRequest();
        request.addEventListener("readystatechange", function() {
            if (request.readyState == 4)
                if (request.status == 200)
                    resolve(JSON.parse(request.responseText).body);
                else if (request.status == 400)
                    reject()
                else
                    throw new Error(`Received status ${request.status} while retrieving CommentID${commentid}`);
        });
        request.open("POST", apiURL.replace("0", commentid));
        request.send();
    });
}
