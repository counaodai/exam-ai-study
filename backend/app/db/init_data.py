PRESET_MODULES = [
    {
        "name": "言语理解与表达",
        "children": [
            {
                "name": "逻辑填空",
                "children": [
                    {"name": "实词辨析"},
                    {"name": "成语辨析"},
                    {"name": "混合辨析"},
                ],
            },
            {
                "name": "片段阅读",
                "children": [
                    {"name": "主旨概括"},
                    {"name": "意图判断"},
                    {"name": "细节理解"},
                    {"name": "态度观点"},
                    {"name": "词句理解"},
                ],
            },
            {
                "name": "语句表达",
                "children": [
                    {"name": "语句排序"},
                    {"name": "语句衔接"},
                    {"name": "下文推断"},
                ],
            },
        ],
    },
    {
        "name": "数量关系",
        "children": [
            {
                "name": "数学运算",
                "children": [
                    {"name": "行程问题"},
                    {"name": "工程问题"},
                    {"name": "排列组合"},
                    {"name": "概率问题"},
                    {"name": "利润问题"},
                    {"name": "容斥原理"},
                    {"name": "几何问题"},
                    {"name": "年龄问题"},
                    {"name": "日期问题"},
                ],
            },
            {
                "name": "数字推理",
                "children": [
                    {"name": "等差数列"},
                    {"name": "等比数列"},
                    {"name": "递推数列"},
                    {"name": "幂次数列"},
                ],
            },
        ],
    },
    {
        "name": "判断推理",
        "children": [
            {
                "name": "图形推理",
                "children": [
                    {"name": "规律类"},
                    {"name": "空间重构"},
                    {"name": "分组类"},
                ],
            },
            {"name": "定义判断"},
            {"name": "类比推理"},
            {
                "name": "逻辑判断",
                "children": [
                    {"name": "削弱题"},
                    {"name": "加强题"},
                    {"name": "前提假设题"},
                    {"name": "结论推出题"},
                    {"name": "真假推理"},
                    {"name": "排列组合推理"},
                ],
            },
        ],
    },
    {
        "name": "资料分析",
        "children": [
            {"name": "增长率"},
            {"name": "增长量"},
            {"name": "比重"},
            {"name": "倍数"},
            {"name": "平均数"},
            {"name": "综合分析"},
        ],
    },
    {
        "name": "常识判断",
        "children": [
            {"name": "政治"},
            {"name": "法律"},
            {"name": "经济"},
            {"name": "历史"},
            {"name": "地理"},
            {"name": "科技"},
            {"name": "文学"},
        ],
    },
]


async def init_preset_modules(db):
    from app.models.module import Module

    for level1 in PRESET_MODULES:
        module1 = Module(name=level1["name"], level=1, is_preset=True)
        db.add(module1)
        await db.flush()

        for level2 in level1.get("children", []):
            module2 = Module(
                name=level2["name"],
                level=2,
                parent_id=module1.id,
                is_preset=True,
            )
            db.add(module2)
            await db.flush()

            for level3 in level2.get("children", []):
                module3 = Module(
                    name=level3["name"],
                    level=3,
                    parent_id=module2.id,
                    is_preset=True,
                )
                db.add(module3)

    await db.commit()
