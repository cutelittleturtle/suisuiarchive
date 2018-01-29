'use strict';

const webpack = require('webpack');
const webpackMerge = require('webpack-merge');
const getCommonConfig = require('./common');

module.exports = webpackMerge(getCommonConfig(), {
  plugins: [
    new webpack.LoaderOptionsPlugin({
      minimize: true,
      debug: false
    }),
    new webpack.optimize.UglifyJsPlugin({
      beautify: false,
      mangle: {
        screw_ie8: true,
        keep_fnames: true
      },
      compress: {
        screw_ie8: true
      },
      comments: false
    })
  ]
});
