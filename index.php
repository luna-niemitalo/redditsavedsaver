<?php 
$files = include("./api/getData.php")

?>

<html>
<link rel="stylesheet" type="text/css" href="style.css">
<body>
<div id="masonry">
</div>
<noscript><img src="https://shynet.itgg.fi/ingress/4dacf587-5295-46ac-abc3-351958ac54ac/pixel.gif"></noscript> <script src="https://shynet.itgg.fi/ingress/4dacf587-5295-46ac-abc3-351958ac54ac/script.js"></script>
<body>
<script src="https://code.jquery.com/jquery-3.5.1.min.js"
    integrity="sha256-9/aliU8dGd2tb6OSsuzixeV4y/faTqgFtohetphbbj0="
    crossorigin="anonymous"></script>
<script type="text/javascript">
    const dataObj = <?php echo($files)?>;
    const data = []
    for (const value in dataObj) {
        data.push(value);
    }
    function imgclick(id) {
        target = "/api/getImage.php?id=" + id;
        window.location.href=target;
    }

    function createBlock(data) {
        const containerBlock = $.parseHTML( "<div class='container'></div>" );
        data.forEach(value => {
        const elementString = `
            <figure>
                <figcaption>${value.id}</figcaption>
                <img src="${"/api/getImage.php?id=" + value.id}" onclick="imgclick('${value.id}')">
            </figure>`;
            const element = $.parseHTML( elementString );
            $(containerBlock).append(element);
        });
        $("#masonry").append(containerBlock);
    }
    data.sort((a, b) => {
        if (b.ts == undefined) {
            b.ts = -10000000000000000;
        }
        if (a.ts == undefined) {
            a.ts = -10000000000000000;
        }

        return a.ts - b.ts;
    });

    var chucks = [];
    var i,j,temparray,chunk = 38;
    for (i=0,j=data.length; i<j; i+=chunk) {
        temparray = data.slice(i,i+chunk);
        chucks.push(temparray);
    }
    let counter = 0;
    createBlock(chucks[counter++]);

    $(window).scroll(function() {
		
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight  - 300) {
        // you're at the bottom of the page
            createBlock(chucks[counter++]);
        }
	});
</script>
<html>