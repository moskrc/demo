({
    appDir: '.',
    baseUrl: '.',
    name: 'main',
    out: 'designer.js',

    paths:{
        plugins: 'empty:',
        jquery: "../assets/js/libs/jquery",
        jqueryui: "../assets/js/libs/jquery-ui",
        jqueryform: "../assets/js/libs/jquery.form",
        lodash:"../assets/js/libs/lodash",
        fileupload:'../assets/js/libs/jquery-file-upload/js/jquery.fileupload',
        "jquery.ui.widget":'../assets/js/libs/jquery-file-upload/js/vendor/jquery.ui.widget',
        jqueryform: '../assets/js/libs/jquery.form',

        // TODO: Can't add to uglified file :(
        backbone:"empty:",
        bootstrap:"empty:"
    }
})


