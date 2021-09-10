module.exports = {
    publicPath:  (e => e.startsWith('/')?e:'/'+e)('wikimesh'),
    assetsDir: "./static",
    outputDir: "./dist/",
    devServer: {
        proxy: "http://wikimesh_app:5000"
    },
    lintOnSave: true
};
