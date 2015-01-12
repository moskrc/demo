// Library paths
require.config({
    paths: {
        jquery: "../assets/js/libs/jquery",
        jqueryui: "../assets/js/libs/jquery-ui",
        jqueryform: "../assets/js/libs/jquery.form",
        bootstrap: "../assets/js/libs/bootstrap",
        lodash: "../assets/js/libs/lodash",
        fileupload: '../assets/js/libs/jquery-file-upload/js/jquery.fileupload',
        "jquery.ui.widget": '../assets/js/libs/jquery-file-upload/js/vendor/jquery.ui.widget',
        jqueryform: '../assets/js/libs/jquery.form',
    }
});
require(['main']);

