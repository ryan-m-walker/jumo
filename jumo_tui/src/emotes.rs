const NEUTRAL_SMILE: &str = r"

▟█▙             ▟█▙
▜█▛             ▜█▛

       ▚▄▄▄▞       
";

const SMIELY: &str = r"

▟█▙             ▟█▙
▜█▛             ▜█▛

       ▜███▛       
";

const HAPPY: &str = r"


▞▀▀▚           ▞▀▀▚

       ▚▄▄▄▞       
";

const SUNGLASSES: &str = r"


▜█████▛▀▀▀▀▀▜█████▛
 █████       █████ 
       ▚▄▄▄▞       
";

const WINK: &str = r"

▟█▙                
▜█▛           ▀▀▀▀▀

       ▚▄▄▄▞       
";

const NEUTRAL: &str = r"

▟█▙             ▟█▙
▜█▛             ▜█▛

       ▄▄▄▄▄       
";

const EXPRESSIONLESS: &str = r"


▀▀▀▀           ▀▀▀▀

       ▄▄▄▄▄       
";

const SMILE: &str = r"


▞▀▀▚           ▞▀▀▚

       ▜███▛       
";

const SWEAT_SMILE: &str = r"

                         ▟▙
    ▞▀▀▚           ▞▀▀▚  ▀▀

           ▜███▛           
";

const UPSIDE_DOWN: &str = r"

       ▞▀▀▀▚       

▟█▙             ▟█▙
▜█▛             ▜█▛
";

pub fn get_emote(emote: &str) -> &str {
    match emote {
        "NEUTRAL_SMILE" => NEUTRAL_SMILE,
        "SMILEY" => SMIELY,
        "HAPPY" => HAPPY,
        "SUNGLASSES" => SUNGLASSES,
        "WINK" => WINK,
        "NEUTRAL" => NEUTRAL,
        "EXPRESSIONLESS" => EXPRESSIONLESS,
        "SMILE" => SMILE,
        "SWEAT_SMILE" => SWEAT_SMILE,
        "UPSIDE_DOWN" => UPSIDE_DOWN,
        _ => "???",
    }
}

pub const ALL_EMOTES: [&str; 10] = [
    "NEUTRAL_SMILE",
    "SMILEY",
    "HAPPY",
    "SUNGLASSES",
    "WINK",
    "NEUTRAL",
    "EXPRESSIONLESS",
    "SMILE",
    "SWEAT_SMILE",
    "UPSIDE_DOWN",
];
