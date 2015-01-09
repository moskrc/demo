exports.config = {
    seleniumAddress: 'http://localhost:4444/wd/hub',
    specs: ['spec.js','challenge_spec.js'],
    rootElement: '#main_app',
    multiCapabilities: [
        {  browserName: 'chrome'},
        {  browserName: 'firefox' }
    ]
}