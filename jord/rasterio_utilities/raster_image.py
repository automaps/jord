from geopandas import GeoDataFrame


__all__ = ["raster_window"]


def raster_window(
    window_min_x,
    window_min_y,
    window_size_x,
    window_size_y,
    image_resolution_x,
    image_resolution_y,
    features,
    window_features,
):
    window_df = GeoDataFrame({"geometry": window_features})

    # Creates upscaled resolution to initially create image
    # Then it is scaled down
    # This is done for higher quality output image
    upscaled_resolution_x = image_resolution_x * 4
    upscaled_resolution_y = image_resolution_y * 4

    # Scales up geometries to fit the image resolution and translates the geometries to have minimum at (0,0)
    x_scale = upscaled_resolution_x / window_size_x
    y_scale = upscaled_resolution_x / window_size_x
    x_offset = -window_min_x * upscaled_resolution_x / window_size_x
    y_offset = -window_min_y * upscaled_resolution_y / window_size_y

    affine_transformation_matrix = [x_scale, 0, 0, y_scale, x_offset, y_offset]
    window_df["transformed_geometry"] = window_df["geometry"].affine_transform(
        affine_transformation_matrix
    )

    rasterized = features.rasterize(
        window_df["transformed_geometry"].tolist(),
        out_shape=(upscaled_resolution_x, upscaled_resolution_y),
        fill=1,
        out=None,
        all_touched=True,
        default_value=0,
        dtype=None,
    )

    return rasterized
