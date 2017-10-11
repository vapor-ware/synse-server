this directory is the location where the configuration should be
placed for synse. 

while we could place it directly in the project root, having it as
a subdirectory makes it easier to add configs via volume mount or 
k8s configmaps.
