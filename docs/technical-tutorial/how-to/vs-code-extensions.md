# Auto-installing VS Code Extensions

Practicus AI Workers can automatically install VS Code extensions every time you start a new Worker,
even without internet access.

## How it Works

By placing downloaded `.vsix` extension files into your extensions directory,
Practicus AI ensures that they are installed in the background the next time VS Code starts inside a Worker.

## Steps

1. Open the open-source VS Code extensions store, [Open VSX](https://open-vsx.org).

   *(This is the same marketplace used when installing directly from the VS Code `Extensions` pane.)*

2. Search for the extension you want, then click **Download**. If asked,

   * Choose **Linux X64**
   * Or, choose **Linux ARM** if you are running on an ARM-based Practicus AI Worker.

3. Save the downloaded `.vsix` file into the extensions folder `~/my/settings/extensions/`

4. To test: create a new Worker and open VS Code.

   > Since extensions are installed in the background, you may need to click **Extensions**
     and then **Reload Window** to complete activation.

## Shared extensions

To save on disk space and avoid downloading the same extension multiple times, an admin can create 
and upload extensions in a **shared extensions folder**.

All `.vsix` files placed into the shared directory (for example, `~/shared/extensions/`) can be symlinked into each user’s personal folder (`~/my/settings/extensions/`).

Example setup:

Run the below inside the worker to create a symlink to a shared extension.

```bash
ln -s ~/shared/extensions/some_extension.vsix ~/my/settings/extensions/
```

To link all extensions

```bash
ln -s ~/shared/extensions/*.vsix ~/my/settings/extensions/
```

After this, each Worker will automatically install extensions from the shared folder via the symlinks
and updating a .vsix file in the shared folder instantly updates it for all users.


---

**Previous**: [View Stats](view-stats.md) | **Next**: [Work With Connections](work-with-connections.md)
