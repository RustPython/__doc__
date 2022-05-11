use once_cell::sync::Lazy;
use std::collections::HashMap;

pub type Result<'a> = std::result::Result<Option<&'a str>, ()>;

pub struct Database<'a> {
    inner: HashMap<&'a str, Option<&'a str>>,
}

impl<'a> Database<'a> {
    pub fn shared() -> &'static Self {
        static DATABASE: Lazy<Database> = Lazy::new(|| {
            let data = include!("../docs.inc.rs");
            let mut map = HashMap::with_capacity(data.len());
            for (item, doc) in data {
                map.insert(item, doc);
            }
            Database { inner: map }
        });
        &DATABASE
    }

    pub fn try_path(&self, path: &str) -> Result {
        self.inner.get(path).copied().ok_or(())
    }

    pub fn try_module_item(&self, module: &str, item: &str) -> Result {
        self.try_path(&format!("{}.{}", module, item))
    }
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn test_module_item() {
        let doc = Database::shared()
            .try_module_item("array", "_array_reconstructor")
            .unwrap();
        assert!(doc.is_some());
    }
}
