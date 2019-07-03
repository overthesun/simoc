const path = require("path");

module.exports ={
    assetsDir: 'static', // For simple configuration of static files in Flask (the "static_folder='client/dist/static'" part in app.py)
    devServer: {
        proxy: 'http://localhost:8000' // So that the client dev server can access your Flask routes
    },
    css:{
        loaderOptions:{
            sass:{
                data: `
                    @import "@/sass/global.scss";
                `
            }
        }
    }
};