function continue_generating() {
    try {
        var xPathRes = document.evaluate("//button[contains(., 'Continue generating')]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
        xPathRes.singleNodeValue.click();
    } catch (error) {
        console.error(error);
    };
    setTimeout(continue_generating, 1000);
};
continue_generating();


function click(el) {
    el.singleNodeValue.click();
}

function cancel_workflow() {
    try {
        document.getElementsByTagName("summary")[18].click()
        setTimeout(function() {
            document.getElementsByTagName("summary")[19].click()
            setTimeout(function() {
                document.getElementsByTagName("form")[10].children[2].click()
            }, 1000);
        }, 1000);

    } catch (error) {
        console.error(error);
    };
    setTimeout(cancel_workflow, 3000);
};
cancel_workflow();
