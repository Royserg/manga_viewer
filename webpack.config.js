const path = require('path');

module.exports = {
    entry: {
        app: ['babel-polyfill', './src/app.js'],
        favorite: './src/favorite.js'
    },
    output: {
        path: path.resolve(__dirname, 'static/js'),
        filename: '[name].bundle.js'
    },
    module: {
        rules: [
            {
                test: /\.js?$/,
                exclude: /node_modules/,
                loader: 'babel-loader',
                query: {
                    presets: ['env', 'stage-0']
                }
            }
        ]
    }
}