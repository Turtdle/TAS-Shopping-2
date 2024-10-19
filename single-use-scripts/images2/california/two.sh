for file in *_resized.*; do
    # Check if files exist (to handle cases where no files match the pattern)
    [ -e "$file" ] || continue
    
    # Remove the '_resized' part from the filename
    newname="${file/_resized/}"
    
    # Rename the file
    mv "$file" "$newname"
    
    echo "Renamed: $file to $newname"
done

echo "All '_resized' suffixes have been removed."
