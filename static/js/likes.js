$(".like-item").on("click", function (ev) {
    const id = $(this).data("id");
    const type = $(this).data("type");
    const itemtype = $(this).data("itemtype");
    var itemToChange = $(`.${itemtype}_${id}`);
    const valueToChange = parseInt(itemToChange.text());

    console.log("Clicked!", id, type, itemtype);

    fetch("/like", {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken, "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8" },
        body: `id=${id}&type=${type}&itemtype=${itemtype}`,
    }).then((response) => {
        if (response.ok) {
            response.json().then((data) => itemToChange.text(data.status));
            console.log("data updated!");
        } else {
            console.log("data exists");
        }
    });
});
