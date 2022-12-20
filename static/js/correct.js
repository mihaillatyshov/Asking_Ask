$(".correct").click(function () {
    const id = $(this).data("id");
    const newValue = this.checked;
    this.checked = !this.checked;
    console.log(this.checked);
    fetch("/correct", {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken, "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8" },
        body: `id=${id}&correct=${newValue}`,
    }).then((response) => {
        if (response.ok) {
            response.json().then((data) => {
                this.checked = data.correct;
            });
            console.log("data updated!");
        }
    });
});
